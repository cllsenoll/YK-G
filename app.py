import streamlit as st
import pandas as pd
import io
import plotly.express as px
import plotly.graph_objects as go
import os
import base64
import re
from fpdf import FPDF

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
if 'f4_df' not in st.session_state:
    st.session_state.f4_df = None
if 'f4_unmatched' not in st.session_state:
    st.session_state.f4_unmatched = None
if 'f4_manual_rows' not in st.session_state:
    st.session_state.f4_manual_rows = {}

# Güncellenmiş ve Düzenlenmiş Firma - Personel Eşleştirme Sözlüğü
if 'firma_personel_map' not in st.session_state:
    st.session_state.firma_personel_map = {
        "ACH DIŞ TİCARET SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SERGEN GÖRÜROĞLU",
        "AKSUN AĞAÇ AMBALAJ KERESTE SAN. TİC.LTD.ŞTİ": "ALATTİN CEBECİ",
        "ALTINSOY MADENCİLİKVE TİCARET A.Ş.": "CELAL ŞENOL",
        "ARMENDUS OPERATÖR KOL VE PANO SİSTEMLERİ SANAYİ VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
        "ARTEA DIŞ TİCARET MAKİNA SANAYİ LİMİTED ŞİRKETİ": "ALATTİN CEBECİ",
        "AYDEMİR DERİ SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SERGEN GÖRÜROĞLU",
        "BAYAGRO TARIM İLAÇLARI SANAYİ VE TİCARETLTD. ŞTİ.": "ALATTİN CEBECİ",
        "BEREKET İLAÇ KOZMETİK SANAYİ VE TİCARET ANONİM ŞİRKETİ": "ALATTİN CEBECİ",
        "BURKON MOBİLYA SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "ALATTİN CEBECİ",
        "BURSA DERİ İHTİSAS VE KARMA ORGANİZE SANAYİ BÖLGESİ": "SERGEN GÖRÜROĞLU",
        "BURSA JELATİN GIDA SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SERGEN GÖRÜROĞLU",
        "BİLEKLER İNŞAAT MAKİNALARI SANAYİ VETİCARET LTD.ŞTİ.": "HASAN SAĞLAM",
        "DEMİRCİOĞLU ŞASE ENDÜSTRİYEL YAĞ OTOMOTİV TEKSTİL GIDA İNŞAAT SANAYİ VE TİCARET A.Ş.": "ALATTİN CEBECİ",
        "DİGİTORİUM ELEKTRONİK TEKNOLOJİLERİ ANONİM ŞİRKETİ": "HASAN SAĞLAM",
        "EKSAGATE ELEKTRONİK MÜHENDİSLİK VE BİLGİSAYAR SANAYİ TİCARET ANONİM ŞİRKETİ-GOSB": "CELAL ŞENOL",
        "ELECTRA GRUP MÜHENDİSLİK ELEKTRİK TAAHHÜT MEKANİK PANO İMALAT İTHALAT İHRACAT SANAYİ VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
        "ELECTRA KABLOSİSTEMLERİ SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "HASAN SAĞLAM",
        "ELECTRA PROJE ELEKTRİK MÜHENDİSLİK TAAHHÜT İNŞAAT ARAÇ KİRALAMA İTHALAT İHRACAT VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
        "ENDER DURSAK": "CELAL ŞENOL",
        "F.S.K.MAKİNE İMALATTAAH.VE GIDA TEKN.SAN.T.LTD.ŞTİ.": "HASAN SAĞLAM",
        "FLY MOBİLYA SANAYİ VE TİCARET ANONİM ŞİRKETİ": "ALATTİN CEBECİ",
        "IPM GALVANO YÜZEY KAPLAMA SANAYİ VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
        "KCL LOJİSTİK OTOMOTİV SANAYİ TİCARET LİMİTED ŞİRKETİ": "ALATTİN CEBECİ",
        "KOLİSAN AMBALAJ SANAYİ VE TİCARET A.Ş.": "ALATTİN CEBECİ",
        "KÜBRA AYDEMİR": "AHMET BERKAN ÖKSÜZ",
        "LİGNUM AĞAÇ MAKİNELERİ SANAYİ TİCARET LİMİTED ŞİRKETİ": "HASAN SAĞLAM",
        "M-BEND METAL ÇELİK MAKİNA İNŞAAT SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "ALATTİN CEBECİ",
        "MAVİFORM METAL KALIPFİKSTÜR VE APARAT SAN.VE TİC.LTD": "ALATTİN CEBECİ",
        "MERZE MOBİLYA TASARIM İNŞAAT SANAYİ TİCARET ANONİM ŞİRKETİ": "ALATTİN CEBECİ",
        "MOGA DERİ MOBİLYA AHŞAP SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
        "MORKİM KİMYA İNŞAAT İTHALAT İHRACAT SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
        "MURSAN FİBERGLASS VE DENİZ ARAÇLARI TURİZM SANAYİ TİCARET PAZARLAMA LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
        "MUSA TEKNOBİLİŞİM BURSA": "MEHMET KAYMAZ",
        "MUVA TEKSTİL SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "CELAL ŞENOL",
        "NARVİN TEKSTİL EMLAK KOZMETİK SOSYAL MEDYA İHRACAT İTHALAT SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "CELAL ŞENOL",
        "NEFES DERİ TEKSTİL OTOMOTİV SANAYİ VE TİCARE T LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
        "NOVMA KİMYA SANAYİ TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
        "SELFİE TARIMSAL TEDARİK SERACILIK DEPOCULUK DANIŞMANLIK SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "CELAL ŞENOL",
        "SERKAN KUYUMCU": "AHMET BERKAN ÖKSÜZ",
        "TUBA ÖZCAN": "SUAT ARI",
        "TURKAUTO MOTORLU ARAÇLAR SANAYİ VE TİCARET LİMİTED ŞİRKETİ.": "HASAN SAĞLAM",
        "VİYA OTOMOTİV CAM TURİZM DENİZCİLİK SANAYİ VE TİCARET LTD. ŞTİ.": "HASAN SAĞLAM",
        "YERLİYURT MARİN DENİZ ARAÇ KAB.TUR.SVE P.LTD.ŞTİ.": "SUAT ARI",
        "YILDIZ GRUBU DERİ KİMYA İNŞAAT TARIM SANAYİ VE DIŞ TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
        "ÖZBAYRAK KIZAK KORUMA SİSTEMLERİ ENDÜSTRİ MAKİNE SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SUAT ARI",
        "İDEA ENDÜSTRİYEL KİMYA SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
        "İNVENTA GIDA SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU"
    }

KULLANICI_ISIM = "Celal ŞENOL"
KULLANICI_GOREV = "Şube Şefi"

# --- CSS VE TRANSLATE KORUMA KODLARI ---
custom_css = """
<style>
    .notranslate { translate: no !important; }
    .stApp { background-color: #070E1E; color: #FFFFFF; }
    h1, h2, h3, h4, h5, h6, p, span, label { color: #FFFFFF !important; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    [data-testid="stSidebar"] { background-color: #0B172E !important; border-right: 1px solid rgba(255, 255, 255, 0.08); }
    [data-testid="stSidebar"] div.stButton > button {
        width: 100% !important; height: 48px !important; border-radius: 10px !important;
        font-weight: 600 !important; background: linear-gradient(135deg, #0A58CA 0%, #032057 100%) !important;
        color: #FFFFFF !important; border: 1px solid rgba(255, 255, 255, 0.15) !important;
        margin-bottom: 6px !important; text-align: left !important; padding-left: 15px !important;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        background: linear-gradient(135deg, #0D6EFD 0%, #0A58CA 100%) !important;
        border-color: #F57C00 !important;
    }
    .person-card {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px; padding: 16px 20px; margin-bottom: 14px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .profile-section { display: flex; align-items: center; gap: 12px; }
    .avatar-circle { width: 62px; height: 62px; border-radius: 50%; border: 2px solid #F57C00; object-fit: cover; background-color: #0B172E; }
    .person-name { font-size: 15px; font-weight: 700; color: #FFFFFF !important; }
    .metric-title { font-size: 11px; color: rgba(255, 255, 255, 0.5) !important; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }
    .metric-value { font-size: 19px; font-weight: 700; }
    .kasa-box { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 20px; margin-top: 20px; }
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

def get_courier_photo(courier_name):
    clean_courier = clean_string(courier_name)
    search_dirs = []
    if os.path.exists("kuryeler"): search_dirs.append("kuryeler")
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
                        if file_name_clean == clean_courier or (clean_courier and (file_name_clean in clean_courier or clean_courier in file_name_clean)):
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

    for engine in ['openpyxl', 'xlrd']:
        try:
            return pd.read_excel(io.BytesIO(file_bytes), engine=engine)
        except Exception:
            continue

    try:
        dfs = pd.read_html(io.BytesIO(file_bytes))
        if dfs and len(dfs) > 0: return dfs[0]
    except Exception:
        pass

    raise Exception("Dosya yapısı çözümlenemedi.")

def process_excel_data(df):
    df.columns = df.columns.astype(str).str.strip()
    req_cols = ["AT Zimmet Personel Adı", "Teslim Eden Personel", "Kargo Teslimat Kanalı"]
    missing_cols = [col for col in req_cols if col not in df.columns]
    if missing_cols: return None, missing_cols

    has_aciklama = "Açıklama" in df.columns

    def check_delivery(row):
        zimmet_p = str(row["AT Zimmet Personel Adı"]).strip().upper()
        teslim_p = str(row["Teslim Eden Personel"]).strip().upper()
        return (zimmet_p == teslim_p) and (zimmet_p != "" and zimmet_p != "NAN")

    def get_channel_type(row):
        kanali = str(row["Kargo Teslimat Kanalı"]).strip().upper()
        aciklama = str(row["Açıklama"]).strip().upper() if has_aciklama else ""
        if "KONTROL SENDE" in kanali or "POS ENTEGRASYON" in aciklama: return "KS-PE"
        elif "SMS" in kanali: return "SMS"
        elif "İMZA" in kanali or "IMZA" in kanali: return "İMZA"
        return "DİĞER"

    df["Is_Teslim"] = df.apply(check_delivery, axis=1)
    df["Custom_Channel"] = df.apply(get_channel_type, axis=1)

    summary = []
    for person in df["AT Zimmet Personel Adı"].dropna().unique():
        p_name = str(person).strip()
        if not p_name or p_name.upper() == "NAN": continue
        p_df = df[df["AT Zimmet Personel Adı"] == person]
        zimmet_cnt = len(p_df)
        teslim_df = p_df[p_df["Is_Teslim"] == True]
        teslim_cnt = len(teslim_df)
        success_rate = round((teslim_cnt / zimmet_cnt) * 100, 1) if zimmet_cnt > 0 else 0.0

        summary.append({
            "Personel": p_name, "Zimmet": zimmet_cnt, "Teslim Edilen": teslim_cnt,
            "Teslim Edilemeyen": zimmet_cnt - teslim_cnt, "Başarı Oranı": success_rate,
            "SMS": len(teslim_df[teslim_df["Custom_Channel"] == "SMS"]),
            "İmza": len(teslim_df[teslim_df["Custom_Channel"] == "İMZA"]),
            "KS-PE": len(teslim_df[teslim_df["Custom_Channel"] == "KS-PE"])
        })
    res_df = pd.DataFrame(summary)
    if not res_df.empty: res_df.index = range(1, len(res_df) + 1)
    return res_df, None

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

    p_col, ft_col, odeme_col, banka_col = None, None, None, None
    for col in df.columns:
        c_upper = str(col).upper()
        if ("PERSONEL" in c_upper or "AD" in c_upper) and not p_col: p_col = col
        elif ("FT" in c_upper or "FATURA" in c_upper) and not ft_col: ft_col = col
        elif ("ÖDEME" in c_upper or "ODEME" in c_upper) and not odeme_col: odeme_col = col
        elif ("BANKA" in c_upper or "ATM" in c_upper) and not banka_col: banka_col = col

    cols_list = list(df.columns)
    if not p_col and len(cols_list) > 0: p_col = cols_list[0]
    if not ft_col and len(cols_list) > 1: ft_col = cols_list[1]
    if not odeme_col and len(cols_list) > 2: odeme_col = cols_list[2]
    if not banka_col and len(cols_list) > 3: banka_col = cols_list[3]

    parsed_rows = []
    for _, row in df.iterrows():
        raw_p_name = str(row[p_col]).strip() if p_col in row else ""
        c_p_name = clean_string(raw_p_name)
        if not c_p_name or c_p_name in ["NAN", "NONE", "TOTAL", "TOPLAM"]: continue
        parsed_rows.append({
            "Raw_Name": raw_p_name, "Clean_Name": c_p_name,
            "Nakit Ft Tutarı Topl": parse_turkish_float(row[ft_col]) if ft_col in row else 0.0,
            "Nakit Ödeme Tutarı Topl": parse_turkish_float(row[odeme_col]) if odeme_col in row else 0.0,
            "Banka/ATM": parse_turkish_float(row[banka_col]) if banka_col in row else 0.0
        })

    temp_df = pd.DataFrame(parsed_rows)
    priority_list = ["HATİCE KÜBRA IŞIK", "ALATTİN CEBECİ", "BURCU DÜREN", "AHMET BERKAN ÖKSÜZ", "HASAN SAĞLAM", "MEHMET KAYMAZ", "SUAT ARI", "SERGEN GÖRÜROĞLU"]
    final_rows = []
    processed_clean_names = set()

    for fixed_name in priority_list:
        clean_fixed = clean_string(fixed_name)
        matched_row = None
        if not temp_df.empty:
            exact_match = temp_df[temp_df["Clean_Name"] == clean_fixed]
            if not exact_match.empty: matched_row = exact_match.iloc[0]
            else:
                contains_match = temp_df[temp_df["Clean_Name"].apply(lambda x: clean_fixed in x or x in clean_fixed)]
                if not contains_match.empty: matched_row = contains_match.iloc[0]

        if matched_row is not None:
            final_rows.append({
                "Personel Adı": fixed_name,
                "Nakit Ft Tutarı Topl": float(matched_row["Nakit Ft Tutarı Topl"]),
                "Nakit Ödeme Tutarı Topl": float(matched_row["Nakit Ödeme Tutarı Topl"]),
                "Banka/ATM": float(matched_row["Banka/ATM"])
            })
            processed_clean_names.add(matched_row["Clean_Name"])
        else:
            final_rows.append({
                "Personel Adı": fixed_name, "Nakit Ft Tutarı Topl": 0.0, "Nakit Ödeme Tutarı Topl": 0.0, "Banka/ATM": 0.0
            })

    result_df = pd.DataFrame(final_rows)
    result_df["Hesap"] = result_df["Nakit Ft Tutarı Topl"] + result_df["Nakit Ödeme Tutarı Topl"] - result_df["Banka/ATM"]
    result_df["İşlem"] = False
    result_df.index = range(1, len(result_df) + 1)
    return result_df[["Personel Adı", "Nakit Ft Tutarı Topl", "Nakit Ödeme Tutarı Topl", "Banka/ATM", "Hesap", "İşlem"]]

# Güncellenmiş ve Esnek F4 Veri İşleme Fonksiyonu
def process_f4_data(df, mapping):
    df.columns = df.columns.astype(str).str.strip()
    
    firma_col = None
    borc_col = None
    
    # Başlıkları akıllı arama ile bulma
    for col in df.columns:
        c_clean = clean_string(col)
        if any(k in c_clean for k in ["MUSTERI", "FIRMA", "UNVAN", "AD"]):
            if firma_col is None: firma_col = col
        if any(k in c_clean for k in ["FATURA", "BORC", "TUTAR", "BAKIYE", "BAKİYE"]):
            if borc_col is None: borc_col = col

    cols_list = list(df.columns)
    # Eğer başlık eşleşmezse varsayılan konumları veya veri içeren sütunları dene
    if firma_col is None and len(cols_list) > 0:
        for c in cols_list:
            if df[c].dtype == object:
                firma_col = c
                break
        if firma_col is None: firma_col = cols_list[0]
        
    if borc_col is None and len(cols_list) > 1:
        for c in cols_list:
            if c != firma_col and (df[c].dtype in ['float64', 'int64'] or df[c].astype(str).str.contains(r'\d').any()):
                borc_col = c
                break
        if borc_col is None: borc_col = cols_list[-1]

    clean_map = {clean_string(k): (k, v) for k, v in mapping.items()}
    
    valid_records = []
    unmatched_records = []

    for _, row in df.iterrows():
        raw_firma = str(row[firma_col]).strip() if firma_col in row else ""
        c_firma = clean_string(raw_firma)
        borc_val = parse_turkish_float(row[borc_col]) if borc_col in row else 0.0

        if borc_val <= 0 or not c_firma or c_firma in ["NAN", "NONE", "TOPLAM", "GENELTOPLAM"]:
            continue

        assigned_person = None
        matched_real_name = None

        if c_firma in clean_map:
            matched_real_name, assigned_person = clean_map[c_firma]
        else:
            for map_clean, (map_real, map_pers) in clean_map.items():
                if map_clean in c_firma or c_firma in map_clean:
                    matched_real_name = map_real
                    assigned_person = map_pers
                    break

        if assigned_person:
            valid_records.append({
                "Personel": assigned_person,
                "Müşteri Adı": matched_real_name or raw_firma,
                "Fatura Borcu": borc_val,
                "Açıklama": ""
            })
        else:
            unmatched_records.append({
                "Müşteri Adı": raw_firma,
                "Fatura Borcu": borc_val,
                "Açıklama": ""
            })

    return pd.DataFrame(valid_records), pd.DataFrame(unmatched_records)

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'GORUKLE ACENTE - TAHSILAT LISTESI', 0, 1, 'C')
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Sayfa {self.page_no()}', 0, 0, 'C')

def generate_pdf_bytes(personnel_name, df_subset):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, f'Personel: {personnel_name}', 0, 1, 'L')
    pdf.cell(0, 8, f'Tarih: {pd.Timestamp.now().strftime("%d.%m.%Y")}', 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(10, 88, 202)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(100, 8, 'Musteri Adi', 1, 0, 'C', True)
    pdf.cell(40, 8, 'Fatura Borcu (TL)', 1, 0, 'C', True)
    pdf.cell(50, 8, 'Aciklama', 1, 1, 'C', True)
    pdf.set_font('Arial', '', 9)
    pdf.set_text_color(0, 0, 0)
    for _, row in df_subset.iterrows():
        pdf.cell(100, 7, str(row['Müşteri Adı'])[:50], 1, 0, 'L')
        pdf.cell(40, 7, f"{float(row['Fatura Borcu']):,.2f} TL", 1, 0, 'R')
        pdf.cell(50, 7, str(row['Açıklama'])[:25], 1, 1, 'L')
    return pdf.output(dest='S').encode('latin1')

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
    
    if st.button("📊 Ana Panel"): st.session_state.active_tab = "Ana Panel"
    if st.button("🏃‍♂️ Kurye Performans"): st.session_state.active_tab = "Kurye Performans"
    if st.button("💰 HESAP"): st.session_state.active_tab = "HESAP"
    if st.button("📋 F4 ÖDEME LİSTESİ"): st.session_state.active_tab = "F4 ÖDEME LİSTESİ"

# ==========================================
# VERİ DAĞITIM VE İŞLEME MİMARİSİ
# ==========================================
perf_df = None
raw_df = None

if uploaded_file is not None:
    try:
        raw_df = smart_read_file(uploaded_file)
        cols_str = " ".join([str(c).upper() for c in raw_df.columns])
        fname_upper = uploaded_file.name.upper()

        # 1. AT Zimmet Raporu Kontrolü
        if "AT ZIMMET" in cols_str or "TESLIM EDEN PERSONEL" in cols_str:
            perf_df, _ = process_excel_data(raw_df)
            
        # 2. Personel Hesap Alımı Kontrolü
        elif "NAKIT" in cols_str or "FT" in cols_str or "ODEME" in cols_str or "BANKA" in cols_str:
            processed_acc = process_personnel_account_data(raw_df)
            st.session_state.account_df = processed_acc
            st.session_state.hesap_df = processed_acc.copy()
            
        # 3. F4 Ödeme Listesi Kontrolü (Genişletilmiş ve esnek koşul)
        else:
            valid_f4, unmatched_f4 = process_f4_data(raw_df, st.session_state.firma_personel_map)
            st.session_state.f4_df = valid_f4
            st.session_state.f4_unmatched = unmatched_f4
    except Exception as e:
        st.error(f"❌ Dosya Okuma/İşleme Hatası: {e}")

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
        st.dataframe(perf_df, use_container_width=True)
    else:
        st.info("💡 Sol menüden **AT ZİMMET İZLEME** dosyanızı yükleyerek ana paneli görüntüleyebilirsiniz.")

# ==========================================
# TAB 2: KURYE PERFORMANS PANELİ
# ==========================================
elif st.session_state.active_tab == "Kurye Performans":
    st.title("🏃‍♂️ Kurye Performans Paneli")
    if uploaded_file is not None and perf_df is None:
        try:
            temp_p, _ = process_excel_data(raw_df)
            if temp_p is not None: perf_df = temp_p
        except: pass

    if perf_df is not None and not perf_df.empty:
        for _, row in perf_df.iterrows():
            p_name = row["Personel"]
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
                    <div style="text-align: center;"><div class="metric-title">Zimmet</div><div class="metric-value">{row['Zimmet']}</div></div>
                    <div style="text-align: center;"><div class="metric-title">Teslim Edilen</div><div class="metric-value" style="color: #4CAF50;">{row['Teslim Edilen']}</div></div>
                    <div style="text-align: center;"><div class="metric-title">Teslim Edilemeyen</div><div class="metric-value" style="color: #F44336;">{row['Teslim Edilemeyen']}</div></div>
                    <div style="text-align: center;"><div class="metric-title">Başarı Oranı</div><div class="metric-value" style="color: #F57C00;">%{row['Başarı Oranı']}</div></div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Kurye performans kartlarını görmek için sol menüden **AT ZİMMET İZLEME** dosyasını yükleyin.")

# ==========================================
# TAB 3: HESAP
# ==========================================
elif st.session_state.active_tab == "HESAP":
    st.title("📋 Günlük Personel Hesap Takip Tablosu")
    account_df = st.session_state.account_df
    if account_df is not None:
        if st.sidebar.button("🔄 Tabloyu Sıfırla"): st.session_state.hesap_df = account_df.copy()
        current_df = st.session_state.hesap_df.copy()
        
        edited_output = st.data_editor(
            current_df,
            column_config={
                "Personel Adı": st.column_config.TextColumn("Personel Adı", required=True),
                "Nakit Ft Tutarı Topl": st.column_config.NumberColumn("Nakit Ft Tutarı Topl", format="%.2f ₺"),
                "Nakit Ödeme Tutarı Topl": st.column_config.NumberColumn("Nakit Ödeme Tutarı Topl", format="%.2f ₺"),
                "Banka/ATM": st.column_config.NumberColumn("Banka/ATM", format="%.2f ₺"),
                "Hesap": st.column_config.NumberColumn("Hesap", format="%.2f ₺", disabled=True),
                "İşlem": st.column_config.CheckboxColumn("İşlem (Tamamlandı)", default=False)
            },
            disabled=["Hesap"], use_container_width=True, num_rows="fixed"
        )
        st.session_state.hesap_df = edited_output
    else:
        st.info("💡 Lütfen sol taraftan **PERSONEL HESAP ALIMI EKRANI** dosyanızı yükleyin.")

# ==========================================
# TAB 4: F4 ÖDEME LİSTESİ (ÖZEL İZOLE ENTEGRASYON)
# ==========================================
elif st.session_state.active_tab == "F4 ÖDEME LİSTESİ":
    st.title("📋 F4 Ödeme Listesi ve Müşteri Tahsilat Dağılımı")

    if st.session_state.f4_df is not None and not st.session_state.f4_df.empty:
        f4_main = st.session_state.f4_df
        
        all_personnel = sorted(list(set(st.session_state.firma_personel_map.values()).union(f4_main["Personel"].unique().tolist())))
        
        st.markdown("### 👤 Personel Seçimi")
        selected_person = st.selectbox("Tahsilat Listesini Görüntülemek İçin Personel Seçin", all_personnel)
        
        if selected_person not in st.session_state.f4_manual_rows:
            st.session_state.f4_manual_rows[selected_person] = pd.DataFrame(columns=["Müşteri Adı", "Fatura Borcu", "Açıklama"])

        p_subset = f4_main[f4_main["Personel"] == selected_person][["Müşteri Adı", "Fatura Borcu", "Açıklama"]].copy()
        manual_sub = st.session_state.f4_manual_rows[selected_person]
        
        combined_df = pd.concat([p_subset, manual_sub], ignore_index=True)
        combined_df.index = range(1, len(combined_df) + 1)
        
        st.subheader(f"📌 {selected_person} - Müşteri Tahsilat Listesi")
        edited_list = st.data_editor(
            combined_df,
            column_config={
                "Müşteri Adı": st.column_config.TextColumn("Müşteri Adı", disabled=True),
                "Fatura Borcu": st.column_config.NumberColumn("Fatura Borcu", format="%.2f ₺"),
                "Açıklama": st.column_config.TextColumn("Açıklama")
            },
            use_container_width=True,
            key=f"editor_{selected_person}"
        )
        
        toplam_borc = edited_list["Fatura Borcu"].sum()
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 15px; text-align: center; margin-top: 15px; margin-bottom: 25px;">
            <h3 style="margin: 0; color: #F57C00;">{selected_person} Toplam Fatura Borcu: {toplam_borc:,.2f} ₺</h3>
        </div>
        """, unsafe_allow_html=True)
        
        pdf_bytes = generate_pdf_bytes(selected_person, edited_list)
        st.download_button(
            label=f"📥 {selected_person} - Tahsilat Listesini PDF İndir",
            data=pdf_bytes,
            file_name=f"{selected_person.replace(' ', '_')}_Tahsilat_Listesi.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        # TANIŞMIZ / EŞLEŞMEYEN MÜŞTERİLER BÖLÜMÜ
        unmatched_df = st.session_state.f4_unmatched
        if unmatched_df is not None and not unmatched_df.empty:
            st.markdown("---")
            st.subheader("🚨 Tanımsız / Eşleşmeyen Firmalar Listesi")
            st.caption("Aşağıdaki firmalar sistemde kayıtlı hiçbir personele otomatik atanmamıştır. **'Ekle'** butonuna tıklayarak yukarıda seçili olan personele dahil edebilirsiniz.")
            
            for idx, row in unmatched_df.iterrows():
                cols = st.columns([4, 2, 1])
                cols[0].text(row["Müşteri Adı"])
                cols[1].text(f"{row['Fatura Borcu']:,.2f} ₺")
                if cols[2].button("➕ Ekle", key=f"add_unmatched_{idx}"):
                    new_row = pd.DataFrame([{
                        "Müşteri Adı": row["Müşteri Adı"],
                        "Fatura Borcu": row["Fatura Borcu"],
                        "Açıklama": ""
                    }])
                    st.session_state.f4_manual_rows[selected_person] = pd.concat([st.session_state.f4_manual_rows[selected_person], new_row], ignore_index=True)
                    st.session_state.f4_unmatched = unmatched_df.drop(idx).reset_index(drop=True)
                    st.success(f"✅ {row['Müşteri Adı']} başarıyla {selected_person} adlı personele eklendi.")
                    st.rerun()
    else:
        st.info("💡 Sol menüden **F4 ÖDEME LİSTESİ** dosyanızı yükleyin. Yüklenen veriler diğer panelleri etkilemeyecek ve yalnızca bu panele özel olarak işlenecektir.")
