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
if 'account_df' not in st.session_state:
    st.session_state.account_df = None
if 'hesap_df' not in st.session_state:
    st.session_state.hesap_df = None
if 'kasa_miktari' not in st.session_state:
    st.session_state.kasa_miktari = 0.0
if 'perf_df' not in st.session_state:
    st.session_state.perf_df = None
if 'raw_df' not in st.session_state:
    st.session_state.raw_df = None
if 'f4_uploaded_df' not in st.session_state:
    st.session_state.f4_uploaded_df = None

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
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        margin-top: 20px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# TÜRKÇE PARS VE TEMİZLEME FONKSİYONLARI
# ==========================================
def clean_string(text):
    if pd.isna(text) or not text:
        return ""
    text = str(text).upper().strip()
    replacements = {'İ': 'I', 'I': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O', 'Ç': 'C'}
    for search, replace in replacements.items():
        text = text.replace(search, replace)
    text = re.sub(r'[^A-Z0-9]', '', text)
    return text

def parse_turkish_float(val):
    if pd.isna(val) or val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s or s.upper() in ['NAN', 'NONE', '-', '0', '0.0', '0,0']:
        return 0.0
    s = s.replace(' ', '').replace('₺', '').replace('TL', '')
    if ',' in s and '.' in s:
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s:
        s = s.replace(',', '.')
    try:
        return float(s)
    except:
        return 0.0

# ==========================================
# FİRMALAR.CSV OTOMATİK YÜKLEME VE EŞLEŞTİRME
# ==========================================
@st.cache_data
def load_firmalar():
    if os.path.exists('FİRMALAR.CSV'):
        try:
            df = pd.read_csv('FİRMALAR.CSV', encoding='cp1254', sep=';')
            df.columns = [str(c).strip() for c in df.columns]
            if 'Müşteri Adı' in df.columns and 'Personel' in df.columns:
                sub = df[['Müşteri Adı', 'Personel']].dropna(subset=['Müşteri Adı']).copy()
                sub['Clean_Musteri'] = sub['Müşteri Adı'].apply(clean_string)
                return sub
        except Exception:
            pass
    return pd.DataFrame(columns=['Müşteri Adı', 'Personel', 'Clean_Musteri'])

firmalar_df = load_firmalar()

# ==========================================
# AKILLI VE GELİŞMİŞ DOSYA OKUMA MOTORU
# ==========================================
def smart_read_file(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    filename = uploaded_file.name.lower()
    
    if filename.endswith(('.xlsx', '.xls')):
        try:
            return pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
        except Exception:
            try:
                return pd.read_excel(io.BytesIO(file_bytes), engine='xlrd')
            except Exception:
                pass

    encodings = ['cp1254', 'iso-8859-9', 'utf-8-sig', 'utf-8', 'latin1']
    separators = [';', ',', '\t', None]

    for enc in encodings:
        for sep in separators:
            try:
                engine_type = 'python' if sep is None else None
                df = pd.read_csv(io.BytesIO(file_bytes), sep=sep, encoding=enc, engine=engine_type, on_bad_lines='skip')
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

    raise Exception("Dosya yapısı çözümlenemedi.")

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
# PERSONEL HESAP ALIMI EKRANI PARSER
# ==========================================
def process_personnel_account_data(df):
    header_idx = 0
    for idx, row in df.iterrows():
        row_str = " ".join([str(val).upper() for val in row.values])
        if "PERSONEL" in row_str or "NAKİT" in row_str or "FT" in row_str or "ÖDEME" in row_str:
            header_idx = idx
            break
            
    if header_idx > 0:
        df.columns = df.iloc[header_idx].astype(str).str.strip()
        df = df.iloc[header_idx + 1:].reset_index(drop=True)
    else:
        df.columns = df.columns.astype(str).str.strip()

    cols_to_drop = [c for c in df.columns if "AÇIKLAMA" in str(c).upper() or "ACIKLAMA" in str(c).upper()]
    df = df.drop(columns=cols_to_drop, errors='ignore')

    p_col, ft_col, odeme_col, banka_col = None, None, None, None
    for col in df.columns:
        c_upper = str(col).upper()
        if ("PERSONEL" in c_upper or "AD" in c_upper or "KURYE" in c_upper) and not p_col:
            p_col = col
        elif (("FT" in c_upper or "FATURA" in c_upper) and not ("AD" in c_upper or "ADET" in c_upper)) and not ft_col:
            ft_col = col
        elif ("ÖDEME" in c_upper or "ODEME" in c_upper) and not odeme_col:
            odeme_col = col
        elif ("BANKA" in c_upper or "ATM" in c_upper or "POS" in c_upper) and not banka_col:
            banka_col = col

    cols_list = list(df.columns)
    if not p_col and len(cols_list) > 0: p_col = cols_list[0]
    if not ft_col and len(cols_list) > 1: ft_col = cols_list[1]
    if not odeme_col and len(cols_list) > 2: odeme_col = cols_list[2]
    if not banka_col and len(cols_list) > 3: banka_col = cols_list[3]

    parsed_rows = []
    for _, row in df.iterrows():
        raw_p_name = str(row[p_col]).strip() if p_col else ""
        c_p_name = clean_string(raw_p_name)
        if not c_p_name or c_p_name in ["NAN", "NONE", "TOTAL", "TOPLAM", "GENELTOPLAM"]:
            continue
            
        ft_val = parse_turkish_float(row[ft_col]) if ft_col else 0.0
        odeme_val = parse_turkish_float(row[odeme_col]) if odeme_col else 0.0
        banka_val = parse_turkish_float(row[banka_col]) if banka_col else 0.0

        parsed_rows.append({
            "Raw_Name": raw_p_name,
            "Clean_Name": c_p_name,
            "Nakit Ft Tutarı Topl": ft_val,
            "Nakit Ödeme Tutarı Topl": odeme_val,
            "Banka/ATM": banka_val
        })

    temp_df = pd.DataFrame(parsed_rows)
    priority_list = [
        "HATİCE KÜBRA IŞIK", "ALATTİN CEBECİ", "BURCU DÜREN",
        "AHMET BERKAN ÖKSÜZ", "HASAN SAĞLAM", "MEHMET KAYMAZ",
        "SUAT ARI", "SERGEN GÖRÜROĞLU"
    ]

    final_rows = []
    processed_clean_names = set()

    for fixed_name in priority_list:
        clean_fixed = clean_string(fixed_name)
        matched_row = None
        if not temp_df.empty:
            exact_match = temp_df[temp_df["Clean_Name"] == clean_fixed]
            if not exact_match.empty:
                matched_row = exact_match.iloc[0]
            else:
                contains_match = temp_df[temp_df["Clean_Name"].apply(lambda x: clean_fixed in x or x in clean_fixed)]
                if not contains_match.empty:
                    matched_row = contains_match.iloc[0]

        if matched_row is not None:
            final_rows.append({
                "Personel Adı": fixed_name,
                "Nakit Ft Tutarı Topl": float(matched_row["Nakit Ft Tutarı Topl"]),
                "Nakit Ödeme Tutarı Topl": float(matched_row["Nakit Ödeme Tutarı Topl"]),
                "Banka/ATM": float(matched_row["Banka/ATM"]),
            })
            processed_clean_names.add(matched_row["Clean_Name"])
        else:
            final_rows.append({
                "Personel Adı": fixed_name,
                "Nakit Ft Tutarı Topl": 0.0,
                "Nakit Ödeme Tutarı Topl": 0.0,
                "Banka/ATM": 0.0,
            })

    if not temp_df.empty:
        for _, row in temp_df.iterrows():
            c_name = row["Clean_Name"]
            if c_name not in processed_clean_names:
                final_rows.append({
                    "Personel Adı": row["Raw_Name"],
                    "Nakit Ft Tutarı Topl": float(row["Nakit Ft Tutarı Topl"]),
                    "Nakit Ödeme Tutarı Topl": float(row["Nakit Ödeme Tutarı Topl"]),
                    "Banka/ATM": float(row["Banka/ATM"]),
                })
                processed_clean_names.add(c_name)

    result_df = pd.DataFrame(final_rows)
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

    uploaded_file = st.file_uploader("📂 Rapor / Liste Yükle (Zimmet veya Hesap)", type=['csv', 'xlsx', 'xls', 'html'])
    
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    if st.button("📊 Ana Panel"):
        st.session_state.active_tab = "Ana Panel"
    if st.button("🏃‍♂️ Kurye Performans"):
        st.session_state.active_tab = "Kurye Performans"
    if st.button("💰 HESAP"):
        st.session_state.active_tab = "HESAP"
    if st.button("📋 F4 ÖDEME LİSTESİ"):
        st.session_state.active_tab = "F4 ÖDEME LİSTESİ"

# ==========================================
# AKILLI VERİ DAĞITIM VE İŞLEME MİMARİSİ
# ==========================================
if uploaded_file is not None:
    try:
        raw_df = smart_read_file(uploaded_file)
        st.session_state.raw_df = raw_df
        
        cols_str = " ".join([str(c).upper() for c in raw_df.columns])
        if "AT ZIMMET" in cols_str or "TESLIM EDEN PERSONEL" in cols_str or "KARGO TESLIMAT KANALI" in cols_str:
            perf_res, _ = process_excel_data(raw_df)
            st.session_state.perf_df = perf_res
            
        elif "NAKIT" in cols_str or "FT" in cols_str or "ODEME" in cols_str or "BANKA" in cols_str or "PERSONEL" in cols_str:
            processed_acc = process_personnel_account_data(raw_df)
            st.session_state.account_df = processed_acc
            st.session_state.hesap_df = processed_acc.copy()
            
    except Exception as e:
        st.error(f"❌ Dosya Okuma/İşleme Hatası: {e}")

# ==========================================
# TAB 1: ANA PANEL
# ==========================================
if st.session_state.active_tab == "Ana Panel":
    st.title("📊 Görükle Acente - Genel Performans Özeti")
    
    perf_df = st.session_state.perf_df
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
            fig_bar = px.bar(perf_df, x="Personel", y="Başarı Oranı", color="Başarı Oranı", color_continuous_scale="RdYlGn", text="Başarı Oranı")
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_right:
            st.subheader("📲 Teslimat Kanalları Dağılımı")
            channel_totals = {"SMS": perf_df["SMS"].sum(), "İmza": perf_df["İmza"].sum(), "KS-PE": perf_df["KS-PE"].sum()}
            fig_pie = px.pie(names=list(channel_totals.keys()), values=list(channel_totals.values()), hole=0.5, color_discrete_sequence=['#0D6EFD', '#F57C00', '#2E7D32'])
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.subheader("📋 Genel Performans Tablosu")
        st.dataframe(perf_df, use_container_width=True)
    else:
        st.info("💡 Sol menüden **AT ZİMMET İZLEME** dosyanızı yükleyerek ana paneli görüntüleyebilirsiniz.")

# ==========================================
# TAB 2: KURYE PERFORMANS PANELİ
# ==========================================
elif st.session_state.active_tab == "Kurye Performans":
    st.title("🏃‍♂️ Kurye Performans Paneli")
    perf_df = st.session_state.perf_df
    if perf_df is not None and not perf_df.empty:
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
                    <div style="text-align: center;"><div class="metric-title">Zimmet Sayısı</div><div class="metric-value" style="color: #FFFFFF;">{zimmet}</div></div>
                    <div style="text-align: center;"><div class="metric-title">Teslim Edilen</div><div class="metric-value" style="color: #4CAF50;">{teslim}</div></div>
                    <div style="text-align: center;"><div class="metric-title">Teslim Edilemeyen</div><div class="metric-value" style="color: #F44336;">{devir}</div></div>
                    <div style="text-align: center; min-width: 80px;"><div class="metric-title">Başarı Oranı</div><div class="metric-value" style="color: #F57C00;">%{rate}</div></div>
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
        st.warning("⚠️ Kurye performans kartlarını görmek için sol menüden AT ZİMMET İZLEME dosyasını yükleyin.")

# ==========================================
# TAB 3: HESAP
# ==========================================
elif st.session_state.active_tab == "HESAP":
    st.title("📋 Günlük Personel Hesap Takip Tablosu")
    account_df = st.session_state.account_df
    if account_df is not None:
        if st.sidebar.button("🔄 Tabloyu Sıfırla"):
            st.session_state.hesap_df = account_df.copy()
            
        current_df = st.session_state.hesap_df.copy()
        def highlight_rows(row):
            if row.get('İşlem', False):
                return ['background-color: rgba(46, 125, 50, 0.4); color: #ffffff; font-weight: bold;'] * len(row)
            return [''] * len(row)

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
            disabled=["Hesap"], hide_index=False, use_container_width=True, num_rows="fixed"
        )

        edited_df = pd.DataFrame(edited_output)
        ft_vals = pd.to_numeric(edited_df["Nakit Ft Tutarı Topl"], errors='coerce').fillna(0.0)
        odeme_vals = pd.to_numeric(edited_df["Nakit Ödeme Tutarı Topl"], errors='coerce').fillna(0.0)
        banka_vals = pd.to_numeric(edited_df["Banka/ATM"], errors='coerce').fillna(0.0)
        edited_df["Hesap"] = ft_vals + odeme_vals - banka_vals
        st.session_state.hesap_df = edited_df

        st.markdown("<div class='kasa-box'>", unsafe_allow_html=True)
        st.subheader("💵 Genel Kasa ve Hesap Dengesi")
        toplam_hesap = float(edited_df["Hesap"].sum())
        col1, col2, col3 = st.columns(3)
        col1.metric("📊 Toplam Hesap", f"{toplam_hesap:,.2f} ₺")
        kasa_val = col2.number_input("🏦 KASA (Manuel Giriniz)", value=float(st.session_state.kasa_miktari), step=100.0, format="%.2f")
        st.session_state.kasa_miktari = kasa_val
        kasa_fark = toplam_hesap - kasa_val
        if kasa_val > toplam_hesap:
            col3.metric("⚖️ Kasa Farkı Durumu", f"{kasa_fark:,.2f} ₺", delta="Durum: AÇIK", delta_color="inverse")
        else:
            col3.metric("⚖️ Kasa Farkı Durumu", f"{kasa_fark:,.2f} ₺", delta="Durum: TAM", delta_color="normal")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("💡 Lütfen sol taraftan PERSONEL HESAP ALIMI EKRANI dosyanızı yükleyin.")

# ==========================================
# TAB 4: F4 ÖDEME LİSTESİ (İSTEDİĞİNİZ TAM ÖZELLİK)
# ==========================================
elif st.session_state.active_tab == "F4 ÖDEME LİSTESİ":
    st.title("📋 F4 Ödeme ve Personel Tahsilat Listesi")
    st.write("F4 Ödeme dosyanızı yükleyin; sistem **FİRMALAR.CSV** verileriyle otomatik eşleştirsin ve seçtiğiniz personele göre anında süzsün.")
    
    st.info(f"Sistemde kayıtlı toplam firma/müşteri eşleşme sayısı (`FİRMALAR.CSV`): **{len(firmalar_df)}**")
    
    # Doğrudan bu sekme içerisinde F4 dosya yükleme alanı
    uploaded_f4 = st.file_uploader("📂 F4 ÖDEME adlı Excel veya CSV dosyanızı yükleyin", type=["csv", "xlsx", "xls"], key="f4_tab_uploader")
    
    if uploaded_f4 is not None:
        try:
            f4_df = smart_read_file(uploaded_f4)
            f4_df.columns = [str(c).strip() for c in f4_df.columns]
            st.session_state.f4_uploaded_df = f4_df
            st.success("✅ F4 Ödeme dosyası başarıyla yüklendi ve hafızaya alındı!")
        except Exception as e:
            st.error(f"❌ Dosya okunurken hata oluştu: {e}")

    if st.session_state.f4_uploaded_df is not None:
        f4_df = st.session_state.f4_uploaded_df
        
        # Müşteri ve Borç sütunlarını akıllıca tespit et
        musteri_kolonu_f4 = None
        borc_kolonu_f4 = None
        
        for col in f4_df.columns:
            col_lower = col.lower()
            if ('müşteri' in col_lower or 'firma' in col_lower or 'unvan' in col_lower or 'ad' in col_lower) and not musteri_kolonu_f4:
                musteri_kolonu_f4 = col
            if ('borç' in col_lower or 'bakiye' in col_lower or 'tutar' in col_lower or 'tahsilat' in col_lower) and not borc_kolonu_f4:
                borc_kolonu_f4 = col
                
        if not musteri_kolonu_f4:
            musteri_kolonu_f4 = f4_df.columns[0]
        if not borc_kolonu_f4 and len(f4_df.columns) > 1:
            borc_kolonu_f4 = f4_df.columns[1]

        # Temiz eşleştirme anahtarı oluştur
        f4_df['Clean_F4_Musteri'] = f4_df[musteri_kolonu_f4].apply(clean_string)
        
        # FİRMALAR ile F4 dosyasını Müşteri Adı üzerinden birleştir (Merge)
        merged_df = pd.merge(
            f4_df, 
            firmalar_df[['Müşteri Adı', 'Personel', 'Clean_Musteri']], 
            how='inner', # Sadece FİRMALAR ile örtüşen müşteriler listelensin
            left_on='Clean_F4_Musteri', 
            right_on='Clean_Musteri'
        )
        
        eslesen_sayisi = len(merged_df)
        st.write(f"📊 F4 dosyasındaki kayıtlardan FİRMALAR listesiyle örtüşen toplam **{eslesen_sayisi}** müşteri bulundu.")
        
        if eslesen_sayisi > 0:
            # Üst Panel: Personel Seçimi (Süzgeç)
            personeller = sorted([p for p in firmalar_df['Personel'].dropna().unique()])
            
            if personeller:
                st.markdown("---")
                secilen_personel = st.selectbox("👤 Üst Panel - Personel Seçimi (Otomatik Süzgeç)", options=personeller)
                
                # Seçilen personele göre filtreleme
                personel_bazli = merged_df[merged_df['Personel'] == secilen_personel].copy()
                
                st.markdown(f"### 📋 {secilen_personel} İçin Örtüşen Müşteriler ve Fatura Borç Listesi")
                
                if not personel_bazli.empty:
                    # Temiz görünümlü sütun düzeni
                    display_cols = [c for c in personel_bazli.columns if c not in ['Clean_F4_Musteri', 'Clean_Musteri']]
                    st.dataframe(personel_bazli[display_cols], use_container_width=True, hide_index=True)
                    
                    # Toplam Fatura Borcu / Tahsilat Hedefi Hesaplama
                    if borc_kolonu_f4 and borc_kolonu_f4 in personel_bazli.columns:
                        temiz_borc = pd.to_numeric(
                            personel_bazli[borc_kolonu_f4].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), 
                            errors='coerce'
                        ).fillna(0)
                        
                        toplam_bakiye = temiz_borc.sum()
                        st.metric(label=f"{secilen_personel} Toplam Fatura Borcu / Tahsilat Hedefi", value=f"{toplam_bakiye:,.2f} ₺")
                    
                    # İndirme Butonu
                    csv_data = personel_bazli[display_cols].to_csv(index=False, encoding='cp1254').encode('cp1254')
                    st.download_button(
                        label=f"📥 {secilen_personel} F4 Tahsilat Listesini İndir (CSV)",
                        data=csv_data,
                        file_name=f"{secilen_personel}_f4_tahsilat_listesi.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning(f"Seçilen personel ({secilen_personel}) için F4 dosyasında örtüşen müşteri kaydı bulunamadı.")
        else:
            st.error("⚠️ F4 dosyasındaki müşteri adları ile FİRMALAR.CSV dosyasındaki müşteri adları eşleşmedi. Lütfen F4 dosyasındaki müşteri sütununu kontrol edin.")
    else:
        st.info("💡 F4 Ödeme analizi ve personel süzgeci için lütfen yukarıdan F4 Ödeme dosyanızı yükleyin.")
