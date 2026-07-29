import streamlit as st
import pandas as pd
import io
import plotly.express as px
import plotly.graph_objects as go
import os
import base64
import re

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(
    page_title="Görükle Acente - Performance Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. OTURUM DURUMU (Session State)
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Ana Panel"

KULLANICI_ISIM = "Celal ŞENOL"
KULLANICI_GOREV = "Şube Şefi"

# --- CSS VE TRANSLATE KORUMA KODLARI ---
custom_css = """
<style>
    .notranslate {
        translate: no !important;
    }
    .stApp {
        background-color: #070E1E;
        color: #FFFFFF;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #FFFFFF !important;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #0B172E !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    [data-testid="stSidebar"] div.stButton > button {
        width: 100% !important;
        height: 48px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #0A58CA 0%, #032057 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        margin-bottom: 6px !important;
        text-align: left !important;
        padding-left: 15px !important;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        background: linear-gradient(135deg, #0D6EFD 0%, #0A58CA 100%) !important;
        border-color: #F57C00 !important;
    }
    .person-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .profile-section {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .avatar-circle {
        width: 62px;
        height: 62px;
        border-radius: 50%;
        border: 2px solid #F57C00;
        object-fit: cover;
        background-color: #0B172E;
    }
    .person-name {
        font-size: 15px;
        font-weight: 700;
        color: #FFFFFF !important;
    }
    .metric-title {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.5) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
    }
    .metric-value {
        font-size: 19px;
        font-weight: 700;
    }
    .channel-badge {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 12px;
        display: inline-block;
        margin-right: 8px;
        margin-top: 8px;
    }
    .badge-val {
        font-weight: 700;
        color: #F57C00 !important;
    }
    .kasa-box {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 18px;
        margin-top: 20px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# İSİM METNİ OTOMATİK NORMALİZASYON FONKSİYONU
# ==========================================
def clean_string(text):
    if not text:
        return ""
    text = str(text).upper().strip()
    replacements = {'İ': 'I', 'I': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O', 'Ç': 'C'}
    for search, replace in replacements.items():
        text = text.replace(search, replace)
    text = re.sub(r'[^A-Z0-9]', '', text)
    return text

# ==========================================
# OTOMATİK KURYE FOTOĞRAFI ALMA
# ==========================================
def get_courier_photo(courier_name):
    clean_courier = clean_string(courier_name)
    
    search_dirs = []
    if os.path.exists("kuryeler"):
        search_dirs.append("kuryeler")
    search_dirs.append(".")

    for target_dir in search_dirs:
        try:
            files = os.listdir(target_dir)
            for file in files:
                file_path = os.path.join(target_dir, file)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file)[1].lower().replace('.', '')
                    if ext in ['png', 'jpg', 'jpeg', 'webp']:
                        file_name_clean = clean_string(os.path.splitext(file)[0])
                        if file_name_clean == clean_courier:
                            try:
                                with open(file_path, "rb") as image_file:
                                    encoded_string = base64.b64encode(image_file.read()).decode()
                                    mime_type = "image/png" if ext == "png" else f"image/{ext}"
                                    return f"data:{mime_type};base64,{encoded_string}"
                            except Exception:
                                pass
        except Exception:
            continue
                        
    return f"https://ui-avatars.com/api/?name={courier_name.replace(' ', '+')}&background=0B172E&color=F57C00&bold=true&size=80"

# ==========================================
# AKILLI DOSYA OKUMA MOTORU
# ==========================================
def smart_read_file(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    encodings = ['cp1254', 'iso-8859-9', 'utf-8-sig', 'utf-8', 'latin1']
    separators = [';', ',', '\t', None]

    for enc in encodings:
        for sep in separators:
            try:
                engine_type = 'python' if sep is None else None
                df = pd.read_csv(
                    io.BytesIO(file_bytes),
                    sep=sep,
                    encoding=enc,
                    engine=engine_type,
                    on_bad_lines='skip'
                )
                if df is not None and len(df.columns) > 1 and len(df) > 0:
                    return df
            except Exception:
                continue

    try:
        return pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
    except Exception:
        pass

    try:
        return pd.read_excel(io.BytesIO(file_bytes), engine='xlrd')
    except Exception:
        pass

    for enc in ['utf-8', 'cp1254', 'latin1']:
        try:
            dfs = pd.read_html(io.BytesIO(file_bytes), encoding=enc)
            if dfs and len(dfs) > 0:
                return dfs[0]
        except Exception:
            continue

    raise Exception("Dosya yapısı çözümlenemedi. Lütfen dosyanın bozuk olmadığını kontrol edin.")

# ==========================================
# AT ZİMMET İZLEME VERİ İŞLEME MOTORU
# ==========================================
def process_excel_data(df):
    df.columns = df.columns.astype(str).str.strip()
    
    req_cols = ["AT Zimmet Personel Adı", "Teslim Eden Personel", "Kargo Teslimat Kanalı"]
    missing_cols = [col for col in req_cols if col not in df.columns]
    
    if missing_cols:
        return None, missing_cols

    has_aciklama = "Açıklama" in df.columns

    def check_delivery(row):
        zimmet_p = str(row["AT Zimmet Personel Adı"]).strip().upper()
        teslim_p = str(row["Teslim Eden Personel"]).strip().upper()
        return (zimmet_p == teslim_p) and (zimmet_p != "" and zimmet_p != "NAN")

    def get_channel_type(row):
        kanali = str(row["Kargo Teslimat Kanalı"]).strip().upper()
        aciklama = str(row["Açıklama"]).strip().upper() if has_aciklama else ""
        
        if "KONTROL SENDE" in kanali or "POS ENTEGRASYON" in aciklama:
            return "KS-PE"
        elif "SMS" in kanali:
            return "SMS"
        elif "İMZA" in kanali or "IMZA" in kanali:
            return "İMZA"
        return "DİĞER"

    df["Is_Teslim"] = df.apply(check_delivery, axis=1)
    df["Custom_Channel"] = df.apply(get_channel_type, axis=1)

    personnel_list = df["AT Zimmet Personel Adı"].dropna().unique()
    summary = []

    for person in personnel_list:
        p_name = str(person).strip()
        if not p_name or p_name.upper() == "NAN":
            continue
            
        p_df = df[df["AT Zimmet Personel Adı"] == person]
        zimmet_cnt = len(p_df)
        
        teslim_df = p_df[p_df["Is_Teslim"] == True]
        teslim_cnt = len(teslim_df)
        teslim_edilemeyen_cnt = zimmet_cnt - teslim_cnt
        
        success_rate = round((teslim_cnt / zimmet_cnt) * 100, 1) if zimmet_cnt > 0 else 0.0
        
        sms_cnt = len(teslim_df[teslim_df["Custom_Channel"] == "SMS"])
        imza_cnt = len(teslim_df[teslim_df["Custom_Channel"] == "İMZA"])
        ks_pe_cnt = len(teslim_df[teslim_df["Custom_Channel"] == "KS-PE"])

        summary.append({
            "Personel": p_name,
            "Zimmet": zimmet_cnt,
            "Teslim Edilen": teslim_cnt,
            "Teslim Edilemeyen": teslim_edilemeyen_cnt,
            "Başarı Oranı": success_rate,
            "SMS": sms_cnt,
            "İmza": imza_cnt,
            "KS-PE": ks_pe_cnt
        })

    res_df = pd.DataFrame(summary)
    if not res_df.empty:
        res_df.index = range(1, len(res_df) + 1)
        
    return res_df, None

# ==========================================
# PERSONEL HESAP ALIMI EKRANI PARSER (DİNAMİK + AKILLI SIRALAMA)
# ==========================================
def process_personnel_account_data(df):
    df.columns = df.columns.astype(str).str.strip()
    
    # "Açıklama" içeren sütunları tamamen kaldır
    cols_to_drop = [c for c in df.columns if "AÇIKLAMA" in c.upper() or "ACIKLAMA" in c.upper()]
    df = df.drop(columns=cols_to_drop, errors='ignore')

    p_col, ft_col, odeme_col, banka_col = None, None, None, None

    for col in df.columns:
        c_upper = col.upper()
        if ("PERSONEL" in c_upper or "AD" in c_upper or "KURYE" in c_upper) and not p_col:
            p_col = col
        elif ("FT" in c_upper or "FATURA" in c_upper) and not ft_col:
            ft_col = col
        elif ("ÖDEME" in c_upper or "ODEME" in c_upper) and not odeme_col:
            odeme_col = col
        elif ("BANKA" in c_upper or "ATM" in c_upper or "POS" in c_upper) and not banka_col:
            banka_col = col

    temp_df = pd.DataFrame()
    temp_df["Personel Adı Raw"] = df[p_col].astype(str).str.strip() if p_col else df.iloc[:, 0].astype(str).str.strip()
    temp_df["Clean_Name"] = temp_df["Personel Adı Raw"].apply(clean_string)

    # Geçersiz/Boş satırları filtrele
    temp_df = temp_df[~temp_df["Clean_Name"].isin(["NAN", "NONE", "TOTAL", "TOPLAM", ""])]
    
    temp_df["Nakit Ft Tutarı Topl"] = pd.to_numeric(df.loc[temp_df.index, ft_col] if ft_col else 0.0, errors='coerce').fillna(0.0)
    temp_df["Nakit Ödeme Tutarı Topl"] = pd.to_numeric(df.loc[temp_df.index, odeme_col] if odeme_col else 0.0, errors='coerce').fillna(0.0)
    temp_df["Banka/ATM"] = pd.to_numeric(df.loc[temp_df.index, banka_col] if banka_col else 0.0, errors='coerce').fillna(0.0)

    # SABİT ÖNCELİKLİ PERSONEL LİSTESİ
    priority_list = [
        "HATİCE KÜBRA IŞIK",
        "ALATTİN CEBECİ",
        "BURCU DÜREN",
        "AHMET BERKAN ÖKSÜZ",
        "HASAN SAĞLAM",
        "MEHMET KAYMAZ",
        "SUAT ARI",
        "SERGEN GÖRÜROĞLU"
    ]

    final_rows = []
    processed_clean_names = set()

    # 1. Önce sabit listedeki isimleri eşleştir ve getir
    for fixed_name in priority_list:
        clean_fixed = clean_string(fixed_name)
        matched = temp_df[temp_df["Clean_Name"] == clean_fixed]
        
        if not matched.empty:
            row = matched.iloc[0]
            final_rows.append({
                "Personel Adı": fixed_name,
                "Nakit Ft Tutarı Topl": float(row["Nakit Ft Tutarı Topl"]),
                "Nakit Ödeme Tutarı Topl": float(row["Nakit Ödeme Tutarı Topl"]),
                "Banka/ATM": float(row["Banka/ATM"]),
            })
            processed_clean_names.add(clean_fixed)
        else:
            # Dosyada o an verisi yoksa varsayılan 0.0 ile ekle
            final_rows.append({
                "Personel Adı": fixed_name,
                "Nakit Ft Tutarı Topl": 0.0,
                "Nakit Ödeme Tutarı Topl": 0.0,
                "Banka/ATM": 0.0,
            })

    # 2. Dosyada bulunan ama sabit listede olmayan Yeni Personelleri Otomatik Sona Ekle
    for _, row in temp_df.iterrows():
        c_name = row["Clean_Name"]
        if c_name not in processed_clean_names:
            final_rows.append({
                "Personel Adı": row["Personel Adı Raw"],
                "Nakit Ft Tutarı Topl": float(row["Nakit Ft Tutarı Topl"]),
                "Nakit Ödeme Tutarı Topl": float(row["Nakit Ödeme Tutarı Topl"]),
                "Banka/ATM": float(row["Banka/ATM"]),
            })
            processed_clean_names.add(c_name)

    result_df = pd.DataFrame(final_rows)
    
    # Formül: Nakit Ft Tutarı Topl + Nakit Ödeme Tutarı Topl - Banka/ATM
    result_df["Hesap"] = result_df["Nakit Ft Tutarı Topl"] + result_df["Nakit Ödeme Tutarı Topl"] - result_df["Banka/ATM"]
    result_df["İşlem"] = False

    result_df.reset_index(drop=True, inplace=True)
    result_df.index = range(1, len(result_df) + 1)

    return result_df[["Personel Adı", "Nakit Ft Tutarı Topl", "Nakit Ödeme Tutarı Topl", "Banka/ATM", "Hesap", "İşlem"]]

# ==========================================
# SIDEBAR VE GEZİNTİ MENÜSÜ
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class="notranslate" style="text-align: center; padding-bottom: 10px;">
        <h2 style="margin: 0; color: #FFFFFF;">Yurtiçi Kargo</h2>
        <h4 style="margin: 0; color: #F57C00;">Görükle Acente KOYS</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="notranslate" style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; margin-bottom: 15px;">
        <small style="color: #F57C00;">Aktif Kullanıcı:</small><br>
        <strong>{KULLANICI_ISIM}</strong> ({KULLANICI_GOREV})
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 Rapor / Liste Yükle", type=None)
    
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    if st.button("📊 Ana Panel"):
        st.session_state.active_tab = "Ana Panel"
    if st.button("🏃‍♂️ Kurye Performans"):
        st.session_state.active_tab = "Kurye Performans"
    if st.button("📋 Günlük Hesap"):
        st.session_state.active_tab = "Günlük Hesap"
    if st.button("📈 Genel Grafikler & Rapor"):
        st.session_state.active_tab = "Genel Raporlama"

# ==========================================
# VERİ YÜKLEME VE İŞLEME AŞAMASI
# ==========================================
perf_df = None
account_df = None
raw_df = None

if uploaded_file is not None:
    try:
        raw_df = smart_read_file(uploaded_file)
        col_names_str = " ".join([str(c).upper() for c in raw_df.columns])
        
        if "AT ZİMMET PERSONEL ADI" in col_names_str or "TESLİM EDEN PERSONEL" in col_names_str:
            perf_df, _ = process_excel_data(raw_df)
        elif "NAKİT" in col_names_str or "BANKA" in col_names_str or "FT" in col_names_str:
            account_df = process_personnel_account_data(raw_df)
        else:
            perf_df, _ = process_excel_data(raw_df)
            account_df = process_personnel_account_data(raw_df)
            
    except Exception as e:
        st.error(f"❌ Dosya Okuma Hatası: {e}")

# ==========================================
# TAB 1: ANA PANEL
# ==========================================
if st.session_state.active_tab == "Ana Panel":
    st.title("📊 Görükle Acente - Genel Performans Özeti")
    
    if perf_df is not None and not perf_df.empty:
        total_zimmet = perf_df["Zimmet"].sum()
        total_teslim = perf_df["Teslim Edilen"].sum()
        total_devir = perf_df["Teslim Edilemeyen"].sum()
        avg_rate = round((total_teslim / total_zimmet) * 100, 1) if total_zimmet > 0 else 0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📦 Toplam Zimmet", f"{total_zimmet:,}")
        c2.metric("✅ Teslim Edilen", f"{total_teslim:,}")
        c3.metric("🚨 Devir / Teslim Edilemeyen", f"{total_devir:,}")
        c4.metric("🎯 Genel Başarı Oranı", f"%{avg_rate}")
        
        st.markdown("---")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("📊 Kurye Başarı Oranları (%)")
            fig_bar = px.bar(
                perf_df, 
                x="Personel", 
                y="Başarı Oranı", 
                color="Başarı Oranı",
                color_continuous_scale="RdYlGn",
                text="Başarı Oranı"
            )
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_right:
            st.subheader("📲 Teslimat Kanalları Dağılımı")
            channel_totals = {
                "SMS": perf_df["SMS"].sum(),
                "İmza": perf_df["İmza"].sum(),
                "KS-PE": perf_df["KS-PE"].sum()
            }
            fig_pie = px.pie(
                names=list(channel_totals.keys()),
                values=list(channel_totals.values()),
                hole=0.5,
                color_discrete_sequence=['#0D6EFD', '#F57C00', '#2E7D32']
            )
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.subheader("📋 Genel Performans Tablosu")
        st.dataframe(perf_df, use_container_width=True)
        
    else:
        st.info("💡 Sol taraftan **AT ZİMMET İZLEME** dosyasını yükleyerek kurye performans paneline erişebilirsiniz.")

# ==========================================
# TAB 2: KURYE PERFORMANS PANELİ
# ==========================================
elif st.session_state.active_tab == "Kurye Performans":
    st.title("🏃‍♂️ Kurye Performans Paneli")
    
    if perf_df is not None and not perf_df.empty:
        st.success(f"✅ AT ZİMMET İZLEME raporu başarıyla işlendi. Toplam **{len(perf_df)}** kurye bulundu.")
        
        for idx, row in perf_df.iterrows():
            p_name = row["Personel"]
            zimmet = row["Zimmet"]
            teslim = row["Teslim Edilen"]
            devir = row["Teslim Edilemeyen"]
            rate = row["Başarı Oranı"]
            sms = row["SMS"]
            imza = row["İmza"]
            ks_pe = row["KS-PE"]

            avatar_url = get_courier_photo(p_name)

            card_html = f"""
            <div class="person-card notranslate">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
                    <div class="profile-section" style="min-width: 220px;">
                        <img src="{avatar_url}" class="avatar-circle">
                        <div>
                            <div class="person-name">{p_name}</div>
                            <small style="color: #F57C00;">Saha Kuryesi</small>
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <div class="metric-title">Zimmet Sayısı</div>
                        <div class="metric-value" style="color: #FFFFFF;">{zimmet}</div>
                    </div>
                    <div style="text-align: center;">
                        <div class="metric-title">Teslim Edilen</div>
                        <div class="metric-value" style="color: #4CAF50;">{teslim}</div>
                    </div>
                    <div style="text-align: center;">
                        <div class="metric-title">Teslim Edilemeyen</div>
                        <div class="metric-value" style="color: #F44336;">{devir}</div>
                    </div>
                    <div style="text-align: center; min-width: 80px;">
                        <div class="metric-title">Başarı Oranı</div>
                        <div class="metric-value" style="color: #F57C00;">%{rate}</div>
                    </div>
                </div>
                <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.06);">
                    <div class="channel-badge">📲 SMS: <span class="badge-val">{sms}</span></div>
                    <div class="channel-badge">✍️ İMZA: <span class="badge-val">{imza}</span></div>
                    <div class="channel-badge">🚪 KS-PE: <span class="badge-val">{ks_pe}</span></div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

    else:
        st.warning("⚠️ Kurye performans kartlarını görmek için sol menüden **AT ZİMMET İZLEME** dosyasını yükleyin.")

# ==========================================
# TAB 3: GÜNLÜK HESAP (ÖNCELİKLİ & DİNAMİK PERSONEL)
# ==========================================
elif st.session_state.active_tab == "Günlük Hesap":
    st.title("📋 Günlük Personel Hesap Takip Tablosu")
    st.caption("✍️ Değerleri değiştirdiğinizde **Hesap (Nakit Ft. Topl + Nakit Ödeme Topl - Banka/ATM)** canlı olarak hesaplanır.")
    
    if account_df is not None:
        if "hesap_df" not in st.session_state or st.sidebar.button("🔄 Dosyadan Yeniden Yükle"):
            st.session_state.hesap_df = account_df.copy()
            
        current_df = st.session_state.hesap_df.copy()

        # Tablo Renklendirme Stili: İşlem True olan satır yeşil renkte vurgulanır
        def highlight_rows(row):
            if row.get('İşlem', False):
                return ['background-color: rgba(46, 125, 50, 0.4); color: #ffffff; font-weight: bold;'] * len(row)
            return [''] * len(row)

        # Interaktif Düzenlenebilir Tek Tablo
        edited_output = st.data_editor(
            current_df.style.apply(highlight_rows, axis=1),
            column_config={
                "Personel Adı": st.column_config.TextColumn("Personel Adı", required=True),
                "Nakit Ft Tutarı Topl": st.column_config.NumberColumn("Nakit Ft Tutarı Topl", format="%.2f ₺"),
                "Nakit Ödeme Tutarı Topl": st.column_config.NumberColumn("Nakit Ödeme Tutarı Topl", format="%.2f ₺"),
                "Banka/ATM": st.column_config.NumberColumn("Banka/ATM", format="%.2f ₺"),
                "Hesap": st.column_config.NumberColumn("Hesap", format="%.2f ₺", disabled=True),
                "İşlem": st.column_config.CheckboxColumn("İşlem (Tamamlandı)", default=False)
            },
            disabled=["Hesap"],
            hide_index=False,
            use_container_width=True,
            num_rows="fixed"
        )

        # KeyError Güvenliği ve Dinamik Hesaplama
        edited_df = pd.DataFrame(edited_output)
        
        ft_vals = pd.to_numeric(edited_df["Nakit Ft Tutarı Topl"], errors='coerce').fillna(0.0) if "Nakit Ft Tutarı Topl" in edited_df.columns else 0.0
        odeme_vals = pd.to_numeric(edited_df["Nakit Ödeme Tutarı Topl"], errors='coerce').fillna(0.0) if "Nakit Ödeme Tutarı Topl" in edited_df.columns else 0.0
        banka_vals = pd.to_numeric(edited_df["Banka/ATM"], errors='coerce').fillna(0.0) if "Banka/ATM" in edited_df.columns else 0.0

        edited_df["Hesap"] = ft_vals + odeme_vals - banka_vals
        st.session_state.hesap_df = edited_df

        # ==========================================
        # TOPLAM HESAP, KASA VE DENGE DURUM BÖLÜMÜ
        # ==========================================
        st.markdown("<div class='kasa-box'>", unsafe_allow_html=True)
        st.subheader("💵 Genel Kasa ve Hesap Dengesi")

        toplam_hesap = float(edited_df["Hesap"].sum())

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("📊 Toplam Hesap", f"{toplam_hesap:,.2f} ₺")

        with col2:
            if "kasa_miktari" not in st.session_state:
                st.session_state.kasa_miktari = 0.0
            kasa_val = st.number_input(
                "🏦 KASA (Manuel Giriniz)", 
                value=float(st.session_state.kasa_miktari), 
                step=100.0, 
                format="%.2f"
            )
            st.session_state.kasa_miktari = kasa_val

        # KASA - Toplam Hesap Hesabı
        kasa_fark = kasa_val - toplam_hesap

        with col3:
            if kasa_fark > 0:
                durum_metni = "AÇIK"
                st.metric("⚖️ Kasa Farkı Durumu", f"{kasa_fark:,.2f} ₺", delta=f"Durum: {durum_metni}", delta_color="inverse")
                st.error(f"🚨 Kasa {kasa_fark:,.2f} ₺ **{durum_metni}** veriyor!")
            else:
                durum_metni = "TAM"
                st.metric("⚖️ Kasa Farkı Durumu", f"{kasa_fark:,.2f} ₺", delta=f"Durum: {durum_metni}", delta_color="normal")
                st.success(f"✅ Kasa hesap dengesi **{durum_metni}**.")

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.info("💡 Lütfen sol taraftan **PERSONEL HESAP ALIMI EKRANI** dosyanızı yükleyin.")

# ==========================================
# TAB 4: GENEL RAPORLAMA VE ANALİZ
# ==========================================
elif st.session_state.active_tab == "Genel Raporlama":
    st.title("📈 Genel Raporlama ve İstatistikler")
    
    if perf_df is not None and not perf_df.empty:
        st.subheader("📊 Kuryeler Arası Zimmet vs Teslimat Karşılaştırması")
        fig_comp = go.Figure(data=[
            go.Bar(name='Teslim Edilen', x=perf_df['Personel'], y=perf_df['Teslim Edilen'], marker_color='#2E7D32'),
            go.Bar(name='Teslim Edilemeyen', x=perf_df['Personel'], y=perf_df['Teslim Edilemeyen'], marker_color='#D32F2F')
        ])
        fig_comp.update_layout(barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_comp, use_container_width=True)
    elif raw_df is not None:
        raw_display = raw_df.copy()
        raw_display.index = range(1, len(raw_display) + 1)
        st.dataframe(raw_display, use_container_width=True)
    else:
        st.info("💡 Grafik analizi için dosya yüklemesi yapın.")
