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

# --- GÖRSELDEKİ ÖZEL KOYU TEMA VE CSS STİLLERİ ---
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

# --- VARSAYILAN (ÖRNEK) VERİ ---
def get_default_data():
    return pd.DataFrame({
        "Kurye": ["Ahmet Berkant Öksüz", "Allattin Cobeci", "Hasan Sağlam", "Mehmet Kaymaz", "Suat Arı"],
        "Zimmet": [266, 250, 247, 246, 240],
        "Teslim": [228, 218, 212, 213, 207],
        "Devir": [37, 32, 35, 33, 33],
        "Sms": [150, 140, 130, 145, 135],
        "İmza": [78, 78, 82, 68, 72],
        "Nakit": [12500.0, 18000.0, 14200.0, 9800.0, 11000.0],
        "Kart": [38000.0, 42000.0, 39000.0, 35000.0, 37480.0]
    })

# --- ESNEK VE AKILLI DOSYA OKUYUCU ---
def load_uploaded_file(file):
    filename = file.name.lower()
    
    if filename.endswith('.csv'):
        # 1. Encoding Tespiti
        raw_data = file.read(20000)
        file.seek(0)
        detected = chardet.detect(raw_data)
        detected_enc = detected['encoding'] if detected['encoding'] else 'iso-8859-9'
        
        encodings = [detected_enc, 'iso-8859-9', 'cp1254', 'utf-8', 'latin1']
        separators = [';', ',', '\t', '|']
        
        # 2. Farklı ayraç ve kodlamaları dene
        for enc in encodings:
            for sep in separators:
                try:
                    file.seek(0)
                    # header=None veya header=0 durumları için engine='python' esnek ayrıştırır
                    df_temp = pd.read_csv(file, encoding=enc, sep=sep, on_bad_lines='skip')
                    if df_temp.shape[1] > 1:
                        return df_temp
                except:
                    continue
        
        # Son Çare: Python motoru ile otomatik sep algılama
        file.seek(0)
        return pd.read_csv(file, encoding='iso-8859-9', sep=None, engine='python', on_bad_lines='skip')
            
    elif filename.endswith('.xlsb'):
        return pd.read_excel(file, engine='pyxlsb')
    elif filename.endswith('.xls'):
        return pd.read_excel(file, engine='xlrd')
    else:
        return pd.read_excel(file)

# --- SÜTUN İSİMLERİNİ OTOMATİK EŞLEŞTİRME VE DÜZELTME ---
def map_columns(df_raw):
    # Eğer üst satırlarda başlık harici açıklamalar varsa, başlık satırını ara
    df_temp = df_raw.copy()
    
    # Sütun adlarını düz stringe çevir
    cols = [str(c).strip() for c in df_temp.columns]
    df_temp.columns = cols
    
    # Sütun adı haritası (Farklı KPOS adlandırmalarını standartlaştırır)
    column_mapping = {}
    
    for c in df_temp.columns:
        c_clean = str(c).strip().lower()
        if any(k in c_clean for k in ['kurye', 'personel', 'dağıtıcı', 'dagitici', 'ad soyad', 'isim']):
            column_mapping[c] = 'Kurye'
        elif any(k in c_clean for k in ['zimmet', 'aldığı', 'aldigi', 'toplam zimmet']):
            column_mapping[c] = 'Zimmet'
        elif any(k in c_clean for k in ['teslim', 'teslimat', 'dağıtılan', 'dagitilan']):
            column_mapping[c] = 'Teslim'
        elif any(k in c_clean for k in ['devir', 'kalan', 'teslim edilmeyen']):
            column_mapping[c] = 'Devir'
        elif 'sms' in c_clean:
            column_mapping[c] = 'Sms'
        elif 'imza' in c_clean or 'i̇mza' in c_clean:
            column_mapping[c] = 'İmza'
        elif 'nakit' in c_clean:
            column_mapping[c] = 'Nakit'
        elif 'kart' in c_clean or 'pos' in c_clean:
            column_mapping[c] = 'Kart'
            
    df_temp = df_temp.rename(columns=column_mapping)
    return df_temp

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
        mapped_df = map_columns(raw_df)
        
        required_cols = ["Kurye", "Zimmet", "Teslim", "Devir"]
        missing_cols = [col for col in required_cols if col not in mapped_df.columns]
        
        if missing_cols:
            st.sidebar.error(f"Eksik Sütunlar: {', '.join(missing_cols)}")
            st.sidebar.info("Mevcut Sütunlar: " + ", ".join(list(raw_df.columns)[:5]) + "...")
            df = get_default_data()
        else:
            num_cols = ["Zimmet", "Teslim", "Devir", "Sms", "İmza", "Nakit", "Kart"]
            for c in num_cols:
                if c in mapped_df.columns:
                    mapped_df[c] = pd.to_numeric(mapped_df[c].astype(str).str.replace(',', '.'), errors="coerce").fillna(0)
                else:
                    mapped_df[c] = 0
            
            df = mapped_df
            st.sidebar.success(f"'{uploaded_file.name}' başarıyla yüklendi!")
            
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
                st.caption(f"Zimmet: **{row['Zimmet']}** | Teslim: **{row['Teslim']}** | Devir: **{row['Devir']}**")

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
        df[["Kurye", "Zimmet", "Teslim", "Devir", "Nakit", "Kart", "Toplam_Tahsilat"]],
        use_container_width=True
    )
