import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import chardet

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Ana Panel - Kargo Operasyon",
    page_icon="📱",
    layout="wide"
)

# --- KOYU TEMA VE CSS STİLLERİ ---
custom_css = """
<style>
    .stApp {
        background-color: #0B1426;
        color: #FFFFFF;
    }
    
    h1, h2, h3, h4, span, label {
        color: #FFFFFF !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .kpi-card-blue {
        background: linear-gradient(135deg, #0A43A6 0%, #002266 100%);
        border-radius: 16px;
        padding: 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 15px;
    }
    
    .kpi-card-orange {
        background: linear-gradient(135deg, #E65100 0%, #F57C00 100%);
        border-radius: 16px;
        padding: 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 15px;
    }

    .kpi-title {
        font-size: 14px;
        opacity: 0.9;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: bold;
    }

    div[data-testid="stFileUploader"] {
        background-color: #121E36;
        border-radius: 10px;
        padding: 10px;
        border: 1px dashed #0A58CA;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- VARSAYILAN (TEST/ÖRNEK) VERİ ---
def get_default_data():
    return pd.DataFrame({
        "Kurye": ["Ahmet Berkant Öksüz", "Allattin Cobeci", "Hasan Sağlam", "Mehmet Kaymaz"],
        "Zimmet": [266, 250, 247, 246],
        "Teslim": [228, 218, 212, 213],
        "Devir": [38, 32, 35, 33],
        "Sms": [150, 140, 130, 145],
        "İmza": [70, 70, 75, 60],
        "KS": [8, 8, 7, 8],
        "Nakit": [0.0, 0.0, 0.0, 0.0],
        "Kart": [0.0, 0.0, 0.0, 0.0]
    })

# --- DOSYA OKUYUCU ---
def load_uploaded_file(file):
    filename = file.name.lower()
    
    if filename.endswith('.csv'):
        raw_data = file.read(20000)
        file.seek(0)
        detected = chardet.detect(raw_data)
        detected_enc = detected['encoding'] if detected['encoding'] else 'iso-8859-9'
        
        encodings = [detected_enc, 'iso-8859-9', 'cp1254', 'utf-8', 'latin1']
        separators = [';', ',', '\t']
        
        for enc in encodings:
            for sep in separators:
                try:
                    file.seek(0)
                    df_temp = pd.read_csv(file, encoding=enc, sep=sep, on_bad_lines='skip')
                    if df_temp.shape[1] > 1:
                        return df_temp
                except:
                    continue
        
        file.seek(0)
        return pd.read_csv(file, encoding='iso-8859-9', sep=None, engine='python', on_bad_lines='skip')
            
    elif filename.endswith('.xlsb'):
        return pd.read_excel(file, engine='pyxlsb')
    elif filename.endswith('.xls'):
        return pd.read_excel(file, engine='xlrd')
    else:
        return pd.read_excel(file)

# --- HAM KPOS VERİSİNİ İŞLEME VE PERFORMANS ÖZETİ OLUŞTURMA ---
def parse_kpos_data(df_raw):
    # Sütun isimlerini temizle
    df_raw.columns = df_raw.columns.astype(str).str.strip()
    
    # Esnek Sütun Yakalama
    col_zimmet_personel = None
    col_teslim_personel = None
    col_durum = None
    col_kanal = None
    col_aciklama = None
    
    for col in df_raw.columns:
        c_clean = col.lower()
        if 'zimmet' in c_clean and 'personel' in c_clean:
            col_zimmet_personel = col
        elif 'teslim' in c_clean and 'personel' in c_clean:
            col_teslim_personel = col
        elif 'durum' in c_clean or 'teslimat durumu' in c_clean:
            col_durum = col
        elif 'kanal' in c_clean:
            col_kanal = col
        elif 'açıklama' in c_clean or 'aciklama' in c_clean:
            col_aciklama = col

    # Eğer ham veri formatı bulunamazsa uyarı ver
    if not col_zimmet_personel:
        return None, "Sütun bulunamadı: 'AT Zimmet Personel Adı'"

    # Personel Listesi (Zimmeti veya Teslimatı olan tüm benzersiz isimler)
    p_zimmet = df_raw[col_zimmet_personel].dropna().astype(str).str.strip().unique()
    p_teslim = df_raw[col_teslim_personel].dropna().astype(str).str.strip().unique() if col_teslim_personel else []
    
    all_personnel = set(p_zimmet).union(set(p_teslim))
    all_personnel = [p for p in all_personnel if p and p.lower() != 'nan' and p != '']

    summary_list = []

    for p in all_personnel:
        # 1. Zimmet Sayısı
        zimmet_mask = df_raw[col_zimmet_personel].astype(str).str.strip() == p
        zimmet_count = int(zimmet_mask.sum())

        # 2. Teslim Sayısı
        if col_teslim_personel:
            teslim_mask = df_raw[col_teslim_personel].astype(str).str.strip() == p
            teslim_count = int(teslim_mask.sum())
        else:
            teslim_mask = pd.Series(False, index=df_raw.index)
            teslim_count = 0

        # 3. Devir Sayısı (Zimmetinde ismi geçen ve Şubede Bekletiliyor olanlar)
        if col_durum:
            devir_mask = zimmet_mask & df_raw[col_durum].astype(str).str.contains('Şubede Bekletiliyor|Teslim Edilmedi', case=False, na=False)
            devir_count = int(devir_mask.sum())
        else:
            devir_count = max(0, zimmet_count - teslim_count)

        # 4. SMS Sayısı
        if col_kanal:
            sms_mask = teslim_mask & df_raw[col_kanal].astype(str).str.upper().str.contains('SMS', na=False)
            sms_count = int(sms_mask.sum())
        else:
            sms_count = 0

        # 5. İMZA Sayısı
        if col_kanal:
            imza_mask = teslim_mask & df_raw[col_kanal].astype(str).str.upper().str.contains('İMZA|IMZA', na=False)
            imza_count = int(imza_mask.sum())
        else:
            imza_count = 0

        # 6. KS Sayısı (KAPIYA BIRAKILDI VEYA POS Entegrasyon)
        ks_by_kanal = (teslim_mask & df_raw[col_kanal].astype(str).str.upper().str.contains('KAPIYA BIRAKILDI', na=False)) if col_kanal else pd.Series(False, index=df_raw.index)
        ks_by_aciklama = (teslim_mask & df_raw[col_aciklama].astype(str).str.contains('POS Entegrasyon', case=False, na=False)) if col_aciklama else pd.Series(False, index=df_raw.index)
        
        ks_count = int((ks_by_kanal | ks_by_aciklama).sum())

        summary_list.append({
            "Kurye": p,
            "Zimmet": zimmet_count,
            "Teslim": teslim_count,
            "Devir": devir_count,
            "Sms": sms_count,
            "İmza": imza_count,
            "KS": ks_count,
            "Nakit": 0.0,
            "Kart": 0.0
        })

    df_summary = pd.DataFrame(summary_list)
    return df_summary, None

# --- VERİ KAYNAĞI PANELİ ---
st.sidebar.title("⚙️ Veri Kaynağı")

uploaded_file = st.sidebar.file_uploader(
    "Dosya Yükleyin (.xlsx, .xls, .xlsm, .xlsb, .csv)", 
    type=None,
    key="universal_excel_uploader"
)

df = None

if uploaded_file is not None:
    try:
        raw_df = load_uploaded_file(uploaded_file)
        
        # Eğer yüklenen dosya zaten özet tablo formatındaysa doğrudan al, değilse ham veriyi işle
        if "Kurye" in raw_df.columns and "Zimmet" in raw_df.columns:
            df = raw_df
            st.sidebar.success(f"'{uploaded_file.name}' özet tablo olarak yüklendi!")
        else:
            parsed_df, err = parse_kpos_data(raw_df)
            if err:
                st.sidebar.error(err)
                df = get_default_data()
            else:
                df = parsed_df
                st.sidebar.success(f"'{uploaded_file.name}' başarıyla analiz edildi!")
            
    except Exception as e:
        st.sidebar.error(f"Dosya okuma hatası: {e}")
        df = get_default_data()
else:
    df = get_default_data()

# --- HESAPLAMALAR ---
df["Zimmet"] = df["Zimmet"].astype(int)
df["Teslim"] = df["Teslim"].astype(int)
df["Devir"] = df["Devir"].astype(int)

df["Teslimat_Orani"] = df.apply(lambda r: (r["Teslim"] / r["Zimmet"] * 100) if r["Zimmet"] > 0 else 0, axis=1)
df["Toplam_Tahsilat"] = df["Nakit"] + df["Kart"]

# --- SEKME YAPISI ---
tab_main, tab_kurye, tab_f4 = st.tabs([
    "🏠 Ana Panel", 
    "👥 Kurye Performansı", 
    "💳 Tahsilat & F4"
])

# ==========================================
# 1. ANA PANEL
# ==========================================
with tab_main:
    st.title("Ana Panel")
    
    toplam_zimmet = int(df["Zimmet"].sum())
    toplam_teslimat = int(df["Teslim"].sum())
    toplam_devir = int(df["Devir"].sum())
    toplam_tahsilat = df["Toplam_Tahsilat"].sum()
    genel_oran = (toplam_teslimat / toplam_zimmet) * 100 if toplam_zimmet > 0 else 0

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.markdown(f"""
            <div class="kpi-card-blue">
                <div class="kpi-title"><span>📦 Zimmet</span> ⚙️</div>
                <div class="kpi-value">{toplam_zimmet:,}</div>
            </div>
        """, unsafe_allow_html=True)

    with row1_col2:
        st.markdown(f"""
            <div class="kpi-card-orange">
                <div class="kpi-title"><span>📝 Teslim Edilen</span> 🚚</div>
                <div class="kpi-value">{toplam_teslimat:,}</div>
            </div>
        """, unsafe_allow_html=True)

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.markdown(f"""
            <div class="kpi-card-blue">
                <div class="kpi-title"><span>🔄 Devir</span> 🔁</div>
                <div class="kpi-value">{toplam_devir:,}</div>
            </div>
        """, unsafe_allow_html=True)

    with row2_col2:
        st.markdown(f"""
            <div class="kpi-card-orange">
                <div class="kpi-title"><span>💳 Tahsilat Tutarı</span> ₺</div>
                <div class="kpi-value">₺{toplam_tahsilat:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Teslimat Oranı")

    fig_donut = go.Figure(data=[go.Pie(
        labels=["Teslim Edilen", "Devir"],
        values=[toplam_teslimat, toplam_devir],
        hole=0.68,
        marker_colors=["#0A58CA", "#FF6B00"],
        textinfo="none"
    )])

    fig_donut.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"),
        showlegend=True,
        height=260,
        margin=dict(l=10, r=10, t=10, b=10),
        annotations=[dict(
            text=f"<b>%{genel_oran:.1f}</b>",
            x=0.5, y=0.5,
            font_size=26,
            font_color="white",
            showarrow=False
        )]
    )

    st.plotly_chart(fig_donut, use_container_width=True)

# ==========================================
# 2. KURYE PERFORMANSI
# ==========================================
with tab_kurye:
    st.title("Kurye Performansı")

    for idx, row in df.iterrows():
        oran = row["Teslimat_Orani"]
        
        with st.container():
            c_img, c_details, c_chart = st.columns([0.8, 2.5, 1.2])
            
            with c_img:
                st.image(f"https://api.dicebear.com/7.x/avataaars/svg?seed={row['Kurye']}", width=55)

            with c_details:
                st.markdown(f"**{row['Kurye']}**")
                st.caption(f"Zimmet: **{row['Zimmet']}** | Teslim: **{row['Teslim']}** | Devir: **{row['Devir']}** | SMS: **{row['Sms']}** | İmza: **{row['İmza']}** | KS: **{row['KS']}**")

            with c_chart:
                fig_mini = go.Figure(data=[go.Pie(
                    values=[oran, max(0, 100 - oran)],
                    hole=0.7,
                    marker_colors=["#FF6B00", "#0A43A6"],
                    textinfo="none"
                )])
                fig_mini.update_layout(
                    showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=70,
                    width=70,
                    margin=dict(l=0, r=0, t=0, b=0),
                    annotations=[dict(
                        text=f"%{oran:.1f}",
                        x=0.5, y=0.5,
                        font_size=12,
                        font_color="white",
                        showarrow=False
                    )]
                )
                st.plotly_chart(fig_mini, use_container_width=False)
            
            st.markdown("<hr style='border-color: #1E2D4A; margin: 5px 0;'>", unsafe_allow_html=True)

# ==========================================
# 3. TAHSİLAT & F4 ÖDEME LİSTESİ
# ==========================================
with tab_f4:
    st.title("Tahsilat & F4 Ödeme Listesi")
    
    st.dataframe(
        df[["Kurye", "Zimmet", "Teslim", "Devir", "Sms", "İmza", "KS", "Nakit", "Kart", "Toplam_Tahsilat"]],
        use_container_width=True
    )
