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

            for file in files:
                file_path = os.path.join(target_dir, file)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file)[1].lower().replace('.', '')
                    if ext in ['png', 'jpg', 'jpeg', 'webp']:
                        file_name_clean = clean_string(os.path.splitext(file)[0])
                        if file_name_clean and clean_courier and (file_name_clean in clean_courier or clean_courier in file_name_clean):
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
# AKILLI VE GELİŞMİŞ DOSYA OKUMA MOTORU
# ==========================================
def smart_read_file(uploaded_file):
    file_bytes = uploaded_file.getvalue()
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
        elif ("FT" in c_upper or "FATURA" in c_upper) and not ft_col:
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

    uploaded_file = st.file_uploader("📂 Rapor / Liste Yükle", type=['csv', 'xlsx', 'xls', 'html'])
    
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
perf_df = None
missing_columns = None
raw_df = None

if uploaded_file is not None:
    try:
        raw_df = smart_read_file(uploaded_file)
        
        # 1. Kontrol: AT Zimmet Raporu mu? (Ana Panel & Kurye Performans için)
        cols_str = " ".join([str(c).upper() for c in raw_df.columns])
        if "AT ZIMMET" in cols_str or "TESLIM EDEN PERSONEL" in cols_str or "KARGO TESLIMAT KANALI" in cols_str:
            perf_df, missing_columns = process_excel_data(raw_df)
            
        # 2. Kontrol: Personel Hesap Alımı Ekranı mı? (HESAP sekmesi için)
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
    
    # Sadece AT Zimmet verisi yüklendiyse burası dolacak
    # Eğer hesap dosyası yüklendiyse perf_df burada boş kalacak ve doğru bilgilendirme dönecek.
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
                te
