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
if 'perf_df' not in st.session_state:
    st.session_state.perf_df = None
if 'f4_df' not in st.session_state:
    st.session_state.f4_df = None
if 'f4_unmatched' not in st.session_state:
    st.session_state.f4_unmatched = None
if 'f4_manual_rows' not in st.session_state:
    st.session_state.f4_manual_rows = {}

KULLANICI_ISIM = "Celal ŞENOL"
KULLANICI_GOREV = "Şube Şefi"

# --- FİRMA - PERSONEL EŞLEŞTİRME SÖZLÜĞÜ ---
FİRMA_PERSONEL_MAP = {
    "ACH DIŞ TİCARET SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "AKSUN AĞAÇ AMBALAJ KERESTE SAN. TİC.LTD.ŞTİ": "ALATTİN CEBECİ",
    "ALTINSOY MADENCİLİKVE TİCARET A.Ş.": "CELAL ŞENOL",
    "ARMENDUS OPERATÖR KOL VE PANO SİSTEMLERİ SANAYİ VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
    "ARTEA DIŞ TİCARET MAKİNA SANAYİ LİMİTED ŞİRKETİ": "ALATTİN CEBECİ",
    "AYDEMİR DERİ SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "BARBAROS BİLİŞİK": "CELAL ŞENOL",
    "BAROMAK MAKİNE SANAYİ TİCARET LİMİTED ŞİRKETİ": "HASAN SAĞLAM",
    "BAYAGRO TARIM İLAÇLARI SANAYİ VE TİCARETLTD. ŞTİ.": "ALATTİN CEBECİ",
    "BAŞATLAR ORMAN ÜRÜNLERİ VE AMBALAJ SAN.TİC.LTD.ŞTİ.": "ALATTİN CEBECİ",
    "BEKA-MAK MAKİNA SANAYİ VE TİCARET A.Ş.": "HASAN SAĞLAM",
    "BEREKET İLAÇ KOZMETİK SANAYİ VE TİCARET ANONİM ŞİRKETİ": "ALATTİN CEBECİ",
    "BES İŞ GÜVENLİK MALZEMELERİ D.T.K.İ.T.K.M.S.V.T.L.ŞT": "HASAN SAĞLAM",
    "BURKON MOBİLYA SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "ALATTİN CEBECİ",
    "BURMOD TEKSTİL SAN.TİC.A.Ş.-BURSA ŞB.": "SERGEN GÖRÜROĞLU",
    "BURSA DERİ İHTİSAS VE KARMA ORGANİZE SANAYİ BÖLGESİ": "SERGEN GÖRÜROĞLU",
    "BURSA JELATİN GIDA SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "BİLEKLER İNŞAAT MAKİNALARI SANAYİ VETİCARET LTD.ŞTİ.": "HASAN SAĞLAM",
    "DEMİRCİOĞLU ŞASE ENDÜSTRİYEL YAĞ OTOMOTİV TEKSTİL GIDA İNŞAAT SANAYİ VE TİCARET A.Ş.": "ALATTİN CEBECİ",
    "DİGİTORİUM ELEKTRONİK TEKNOLOJİLERİ ANONİM ŞİRKETİ": "HASAN SAĞLAM",
    "DOĞANYİĞİTLER ORGANİK GIDA SANAYİ TİCARET LİMİTED ŞİRKETİ": "SUAT ARI",
    "ELECTRA GRUP MÜHENDİSLİK ELEKTRİK TAAHHÜT MEKANİK PANO İMALAT İTHALAT İHRACAT SANAYİ VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
    "ELECTRA KABLOSİSTEMLERİ SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "HASAN SAĞLAM",
    "ELECTRA PROJE ELEKTRİK MÜHENDİSLİK TAAHHÜT İNŞAAT ARAÇ KİRALAMA İTHALAT İHRACAT VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
    "ENDER DURSAK": "CELAL ŞENOL",
    "F.S.K.MAKİNE İMALATTAAH.VE GIDA TEKN.SAN.T.LTD.ŞTİ.": "HASAN SAĞLAM",
    "FLY MOBİLYA SANAYİ VE TİCARET ANONİM ŞİRKETİ": "ALATTİN CEBECİ",
    "HMT MAKİNA SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SUAT ARI",
    "IPM GALVANO YÜZEY KAPLAMA SANAYİ VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
    "KCL LOJİSTİK OTOMOTİV SANAYİ TİCARET LİMİTED ŞİRKETİ": "ALATTİN CEBECİ",
    "KOLİSAN AMBALAJ SANAYİ VE TİCARET A.Ş.": "ALATTİN CEBECİ",
    "KOÇASLANLAR OTOMOTİV İNŞ.TAŞIMA PETROL ÜRGIDA SAN VE TİC A.Ş.-BURSA GÖRÜKLE": "ALATTİN CEBECİ",
    "KURTSAN GIDA SAN VE TİC LTD ŞTİ": "SUAT ARI",
    "KÜBRA AYDEMİR": "AHMET BERKAN ÖKSÜZ",
    "LİGNUM AĞAÇ MAKİNELERİ SANAYİ TİCARET LİMİTED ŞİRKETİ": "HASAN SAĞLAM",
    "LOKMAN KOÇASLAN OTOMOTİV SANAYİ TİCARET LİMİTED ŞİRKETİ": "ALATTİN CEBECİ",
    "M-BEND METAL ÇELİK MAKİNA İNŞAAT SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "ALATTİN CEBECİ",
    "MAVİFORM METAL KALIPFİKSTÜR VE APARAT SAN.VE TİC.LTD": "ALATTİN CEBECİ",
    "MERZE MOBİLYA TASARIM İNŞAAT SANAYİ TİCARET ANONİM ŞİRKETİ": "ALATTİN CEBECİ",
    "MOGA DERİ MOBİLYA AHŞAP SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "MORKİM KİMYA İNŞAAT İTHALAT İHRACAT SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "MURSAN FİBERGLASS VE DENİZ ARAÇLARI TURİZM SANAYİ TİCARET PAZARLAMA LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "MUSA TEKNOBİLİŞİM BURSA": "MEHMET KAYMAZ",
    "MUVA TEKSTİL SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "CELAL ŞENOL",
    "MİNTEKS TEKSTİL SAN VE TİC. LTD.ŞTİ. İŞLETME ADI:MİNTEKS": "SUAT ARI",
    "NARVİN TEKSTİL EMLAK KOZMETİK SOSYAL MEDYA İHRACAT İTHALAT SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "CELAL ŞENOL",
    "NEFES DERİ TEKSTİL OTOMOTİV SANAYİ VE TİCARE T LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "NOVMA KİMYA SANAYİ TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "ORCA HOME TEKSTİL İTHALAT İHRACATSANAYİ VE TİCARET LİMİTED ŞİRKETİ": "SUAT ARI",
    "SELFİE TARIMSAL TEDARİK SERACILIK DEPOCULUK DANIŞMANLIK SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "CELAL ŞENOL",
    "SERKAN KUYUMCU": "AHMET BERKAN ÖKSÜZ",
    "T-BİYOTEKNOLOJİ LABORATUVAR ESTETİK MEDİKAL KOZMETİK SANAYİVE TİCARET LTD.ŞTİ.": "SUAT ARI",
    "TUBA ÖZCAN": "SUAT ARI",
    "TURKAUTO MOTORLU ARAÇLAR SANAYİ VE TİCARET LİMİTED ŞİRKETİ.": "HASAN SAĞLAM",
    "UĞURLU FİNİSAJ SİSTEMLERİ SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SUAT ARI",
    "VARNA DERİ SANAYİ VE TİCARET A.Ş.": "SUAT ARI",
    "VİYA OTOMOTİV CAM TURİZM DENİZCİLİK SANAYİ VE TİCARET LTD. ŞTİ.": "HASAN SAĞLAM",
    "YERLİYURT MARİN DENİZ ARAÇ KAB.TUR.SVE P.LTD.ŞTİ.": "SUAT ARI",
    "YILDIZ GRUBU DERİ KİMYA İNŞAAT TARIM SANAYİ VE DIŞ TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "ÖZBAYRAK KIZAK KORUMA SİSTEMLERİ ENDÜSTRİ MAKİNE SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SUAT ARI",
    "İDEA ENDÜSTRİYEL KİMYA SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "İNVENTA GIDA SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU"
}

# --- CSS ---
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
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# YARDIMCI FONKSİYONLAR
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

    raise Exception("Dosya yapısı çözümlenemedi.")

def process_excel_data(df):
    df.columns = df.columns.astype(str).str.strip()
    req_cols = ["AT Zimmet Personel Adı", "Teslim Eden Personel", "Kargo Teslimat Kanalı"]
    if not all(col in df.columns for col in req_cols):
        return None

    has_aciklama = "Açıklama" in df.columns

    def check_delivery(row):
        return (str(row["AT Zimmet Personel Adı"]).strip().upper() == str(row["Teslim Eden Personel"]).strip().upper())

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
    return res_df

def process_personnel_account_data(df):
    header_idx = 0
    for idx, row in df.iterrows():
        row_str = " ".join([str(val).upper() for val in row.values])
        if "PERSONEL" in row_str or "NAKİT" in row_str or "FT" in row_str:
            header_idx = int(idx)
            break
    df.columns = df.iloc[header_idx].astype(str).str.strip()
    df = df.iloc[header_idx + 1:].reset_index(drop=True)

    p_col, ft_col, odeme_col, banka_col = None, None, None, None
    for col in df.columns:
        c_upper = str(col).upper()
        if "PERSONEL" in c_upper or "AD" in c_upper: p_col = col
        elif "FT" in c_upper or "FATURA" in c_upper: ft_col = col
        elif "ÖDEME" in c_upper or "ODEME" in c_upper: odeme_col = col
        elif "BANKA" in c_upper or "ATM" in c_upper: banka_col = col

    cols_list = list(df.columns)
    if p_col is None and len(cols_list) > 0: p_col = cols_list[0]
    if ft_col is None and len(cols_list) > 1: ft_col = cols_list[1]
    if odeme_col is None and len(cols_list) > 2: odeme_col = cols_list[2]
    if banka_col is None and len(cols_list) > 3: banka_col = cols_list[3]

    parsed_rows = []
    for _, row in df.iterrows():
        raw_p = str(row[p_col]).strip() if p_col in row else ""
        c_p = clean_string(raw_p)
        if not c_p or c_p in ["NAN", "NONE", "TOPLAM"]: continue
        parsed_rows.append({
            "Raw_Name": raw_p, "Clean_Name": c_p,
            "Nakit Ft Tutarı Topl": parse_turkish_float(row[ft_col]) if ft_col in row else 0.0,
            "Nakit Ödeme Tutarı Topl": parse_turkish_float(row[odeme_col]) if odeme_col in row else 0.0,
            "Banka/ATM": parse_turkish_float(row[banka_col]) if banka_col in row else 0.0
        })

    temp_df = pd.DataFrame(parsed_rows)
    final_rows = []
    for fixed_name in ["HATİCE KÜBRA IŞIK", "ALATTİN CEBECİ", "BURCU DÜREN", "AHMET BERKAN ÖKSÜZ", "HASAN SAĞLAM", "MEHMET KAYMAZ", "SUAT ARI", "SERGEN GÖRÜROĞLU"]:
        clean_fixed = clean_string(fixed_name)
        matched = temp_df[temp_df["Clean_Name"] == clean_fixed] if not temp_df.empty else pd.DataFrame()
        if not matched.empty:
            r = matched.iloc[0]
            final_rows.append({"Personel Adı": fixed_name, "Nakit Ft Tutarı Topl": r["Nakit Ft Tutarı Topl"], "Nakit Ödeme Tutarı Topl": r["Nakit Ödeme Tutarı Topl"], "Banka/ATM": r["Banka/ATM"]})
        else:
            final_rows.append({"Personel Adı": fixed_name, "Nakit Ft Tutarı Topl": 0.0, "Nakit Ödeme Tutarı Topl": 0.0, "Banka/ATM": 0.0})

    result_df = pd.DataFrame(final_rows)
    result_df["Hesap"] = result_df["Nakit Ft Tutarı Topl"] + result_df["Nakit Ödeme Tutarı Topl"] - result_df["Banka/ATM"]
    result_df["İşlem"] = False
    result_df.index = range(1, len(result_df) + 1)
    return result_df[["Personel Adı", "Nakit Ft Tutarı Topl", "Nakit Ödeme Tutarı Topl", "Banka/ATM", "Hesap", "İşlem"]]

def process_f4_payment_list(df):
    df.columns = df.columns.astype(str).str.strip()
    
    firma_col = None
    fatura_borcu_col = None

    for col in df.columns:
        c_clean = clean_string(col)
        if "MUSTERI" in c_clean or "FIRMA" in c_clean:
            if firma_col is None: firma_col = col
        if "FATURABORCU" in c_clean or "FATURA" in c_clean:
            if fatura_borcu_col is None: fatura_borcu_col = col

    cols_list = list(df.columns)
    if firma_col is None and len(cols_list) > 2: firma_col = cols_list[2]
    if fatura_borcu_col is None and len(cols_list) > 3: fatura_borcu_col = cols_list[3]

    valid_records = []
    unmatched_records = []
    clean_map = {clean_string(k): (k, v) for k, v in FİRMA_PERSONEL_MAP.items()}

    for _, row in df.iterrows():
        raw_firma = str(row[firma_col]).strip() if firma_col in row else ""
        c_firma = clean_string(raw_firma)
        fatura_val = parse_turkish_float(row[fatura_borcu_col]) if fatura_borcu_col in row else 0.0

        if fatura_val <= 0 or not c_firma or c_firma in ["NAN", "NONE", "TOPLAM"]:
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
            valid_records.append({"Personel": assigned_person, "Firma Adı": matched_real_name or raw_firma, "Fatura Borcu (₺)": fatura_val, "Açıklama": ""})
        else:
            unmatched_records.append({"Firma Adı": raw_firma, "Fatura Borcu (₺)": fatura_val})

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
    pdf.cell(90, 8, 'Firma Adi', 1, 0, 'C', True)
    pdf.cell(40, 8, 'Fatura Borcu (TL)', 1, 0, 'C', True)
    pdf.cell(60, 8, 'Aciklama', 1, 1, 'C', True)
    pdf.set_font('Arial', '', 9)
    pdf.set_text_color(0, 0, 0)
    for _, row in df_subset.iterrows():
        pdf.cell(90, 7, str(row['Firma Adı'])[:45], 1, 0, 'L')
        pdf.cell(40, 7, f"{float(row['Fatura Borcu (₺)']):,.2f} TL", 1, 0, 'R')
        pdf.cell(60, 7, str(row['Açıklama'])[:30], 1, 1, 'L')
    return pdf.output(dest='S').encode('latin1')

# ==========================================
# SIDEBAR
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

    uploaded_files = st.file_uploader("📂 Rapor / Liste Yükle (Çoklu Seçim)", type=['csv', 'xlsx', 'xls', 'html'], accept_multiple_files=True)
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    if st.button("📊 Ana Panel"): st.session_state.active_tab = "Ana Panel"
    if st.button("🏃‍♂️ Kurye Performans"): st.session_state.active_tab = "Kurye Performans"
    if st.button("💰 HESAP"): st.session_state.active_tab = "HESAP"
    if st.button("📋 F4 ÖDEME LİSTESİ"): st.session_state.active_tab = "F4 ÖDEME LİSTESİ"

# ==========================================
# ÇOKLU DOSYA İŞLEME VE OTOMATİK SINIFLANDIRMA
# ==========================================
if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            raw_df = smart_read_file(uploaded_file)
            cols_str = " ".join([str(c).upper() for c in raw_df.columns])
            
            if "AT ZIMMET" in cols_str or "TESLIM EDEN PERSONEL" in cols_str:
                st.session_state.perf_df = process_excel_data(raw_df)
            elif "NAKIT" in cols_str or "FT" in cols_str or "FATURA BORCU" in cols_str and "MÜŞTERİ" not in cols_str:
                processed_acc = process_personnel_account_data(raw_df)
                st.session_state.account_df = processed_acc
                st.session_state.hesap_df = processed_acc.copy()
            else:
                valid_f4, unmatched_f4 = process_f4_payment_list(raw_df)
                if not valid_f4.empty or "FATURA BORCU" in cols_str or "MÜŞTERİ ADI" in cols_str:
                    st.session_state.f4_df = valid_f4
                    st.session_state.f4_unmatched = unmatched_f4
        except Exception as e:
            st.error(f"❌ Dosya Okuma Hatası ({uploaded_file.name}): {e}")

# ==========================================
# SEKME YÖNETİMİ
# ==========================================
if st.session_state.active_tab == "Ana Panel":
    st.title("📊 Görükle Acente - Genel Performans Özeti")
    if st.session_state.perf_df is not None and not st.session_state.perf_df.empty:
        st.dataframe(st.session_state.perf_df, use_container_width=True)
    else:
        st.info("💡 Sol menüden AT Zimmet İzleme raporunuzu yükleyebilirsiniz.")

elif st.session_state.active_tab == "Kurye Performans":
    st.title("🏃‍♂️ Kurye Performans Paneli")
    if st.session_state.perf_df is not None and not st.session_state.perf_df.empty:
        for _, row in st.session_state.perf_df.iterrows():
            st.markdown(f"**{row['Personel']}** - Başarı: %{row['Başarı Oranı']}")
    else:
        st.warning("⚠️ AT ZİMMET raporu yükleyin.")

elif st.session_state.active_tab == "HESAP":
    st.title("📋 Günlük Personel Hesap Takip Tablosu")
    if st.session_state.account_df is not None:
        edited = st.data_editor(st.session_state.hesap_df, use_container_width=True)
        st.session_state.hesap_df = edited
    else:
        st.info("💡 Personel Hesap Alımı ekranı yükleyin.")

elif st.session_state.active_tab == "F4 ÖDEME LİSTESİ":
    st.title("📋 F4 Ödeme Listesi")
    if st.session_state.f4_df is not None and not st.session_state.f4_df.empty:
        f4_main_df = st.session_state.f4_df
        unique_personnel = sorted(f4_main_df["Personel"].unique().tolist())
        
        if unique_personnel:
            st.markdown("Personel Seçin:")
            selected_person = st.selectbox("Personel Seçin", unique_personnel, label_visibility="collapsed")
            p_subset = f4_main_df[f4_main_df["Personel"] == selected_person].copy()
            
            if selected_person not in st.session_state.f4_manual_rows:
                st.session_state.f4_manual_rows[selected_person] = pd.DataFrame(columns=["Firma Adı", "Fatura Borcu (₺)", "Açıklama"])
                
            manual_df = st.session_state.f4_manual_rows[selected_person]
            
            with st.form(key=f"manual_form_{selected_person}", clear_on_submit=True):
                st.subheader("➕ Manuel Firma Satırı Ekle")
                c1, c2, c3 = st.columns([3, 2, 1])
                new_firma = c1.text_input("Firma Adı")
                new_borc = c2.number_input("Fatura Borcu (₺)", min_value=0.0, step=10.0)
                if c3.form_submit_button("Satır Ekle") and new_firma:
                    new_r = pd.DataFrame([{"Firma Adı": new_firma.upper(), "Fatura Borcu (₺)": new_borc, "Açıklama": ""}])
                    st.session_state.f4_manual_rows[selected_person] = pd.concat([manual_df, new_r], ignore_index=True)
                    st.rerun()

            combined_df = pd.concat([p_subset[["Firma Adı", "Fatura Borcu (₺)", "Açıklama"]], manual_df], ignore_index=True)
            combined_df.index = range(1, len(combined_df) + 1)
            
            edited_list = st.data_editor(combined_df, use_container_width=True)
            
            toplam_borc = edited_list["Fatura Borcu (₺)"].sum()
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 15px; text-align: center; margin-top: 15px;">
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
        else:
            st.warning("⚠️ F4 dosyasındaki firmalar eşleşme tablosundaki isimlerle uyuşmadı.")
            
        if st.session_state.f4_unmatched is not None and not st.session_state.f4_unmatched.empty:
            with st.expander("🚨 Eşleşmeyen Firmalar"):
                st.dataframe(st.session_state.f4_unmatched, use_container_width=True)
    else:
        st.info("💡 Sol menüden **F4 ÖDEME LİSTESİ** dosyanızı yükleyin.")
