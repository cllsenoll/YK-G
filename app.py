import streamlit as st
import pandas as pd
import io

# 1. Sayfa Ayarları
st.set_page_config(
    page_title="Yurtiçi Kargo Görükle Acente",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. OTURUM DURUMU (Session State)
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Kurye Performans"

KULLANICI_ISIM = "Celal Şenol"
KULLANICI_GOREV = "Şube Şefi"

# --- CSS ÖZELLEŞTİRMELERİ ---
custom_css = """
<style>
    .stApp {
        background-color: #070E1E;
        color: #FFFFFF;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #FFFFFF !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #0B172E !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    [data-testid="stSidebar"] div.stButton > button {
        width: 100% !important;
        height: 50px !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #0A58CA 0%, #032057 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        margin-bottom: 8px !important;
    }

    /* PERSONEL PERFORMANS KARTI TASARIMI */
    .person-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    .person-main-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 15px;
        padding-bottom: 14px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .profile-section {
        display: flex;
        align-items: center;
        gap: 14px;
        min-width: 220px;
    }
    .avatar-circle {
        width: 65px;
        height: 65px;
        min-width: 65px;
        min-height: 65px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #F57C00;
        background-color: #0B172E;
    }
    .person-name {
        font-size: 16px;
        font-weight: 700;
        color: #FFFFFF !important;
    }
    .metric-box {
        text-align: center;
        flex: 1;
    }
    .metric-title {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.6) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 20px;
        font-weight: 700;
    }
    
    /* YUVARLAK ÇEMBER GRAFİK ALANI */
    .chart-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 65px;
        min-width: 65px;
    }
    .chart-label {
        font-size: 11px;
        font-weight: 700;
        margin-top: 4px;
        color: #4CAF50 !important;
    }

    /* ALT KANAL DETAY ROZETLERİ */
    .channel-row {
        display: flex;
        gap: 12px;
        margin-top: 12px;
        padding-top: 2px;
    }
    .channel-badge {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .badge-value {
        font-weight: 700;
        color: #F57C00 !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- SVG YUVALAK ÇEMBER GRAFİK ÜRETİCİ ---
def generate_pie_svg(success_rate):
    """Yeşil ve Kırmızı renklerden oluşan 65x65 px SVG tam çember grafik oluşturur."""
    rate = max(0, min(100, success_rate))
    if rate == 100:
        return f"""
        <svg width="65" height="65" viewBox="0 0 36 36">
            <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#2E7D32" stroke-width="3.8" />
        </svg>
        """
    elif rate == 0:
        return f"""
        <svg width="65" height="65" viewBox="0 0 36 36">
            <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#D32F2F" stroke-width="3.8" />
        </svg>
        """
    
    stroke_dasharray = f"{rate}, {100 - rate}"
    return f"""
    <svg width="65" height="65" viewBox="0 0 36 36" style="transform: rotate(-90deg); border-radius: 50%;">
        <!-- Kırmızı Arka Plan (Teslim Edilemeyen Oran) -->
        <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#D32F2F" stroke-width="3.8" />
        <!-- Yeşil Ön Plan (Teslim Edilen Oran) -->
        <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#2E7D32" stroke-width="3.8" stroke-dasharray="{stroke_dasharray}" />
    </svg>
    """

# ==========================================
# SIDEBAR (DOSYA YÜKLEME VE MENÜ)
# ==========================================
with st.sidebar:
    st.markdown("### Yurtiçi Kargo<br><small style='color:#F57C00;'>Görükle Acente</small>", unsafe_allow_html=True)
    st.write("")
    
    uploaded_file = st.file_uploader("AT ZİMMET İZLEME Dosyası Yükle", type=["xlsx", "xls", "csv"])
    
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    if st.button("🏃‍♂️ Kurye Performans"):
        st.session_state.active_tab = "Kurye Performans"

# ==========================================
# VERİ İŞLEME MOTORU (EXCEL PARSER)
# ==========================================
def process_excel_data(df):
    # Kolon İsimlerini Temizle
    df.columns = df.columns.str.strip()
    
    # Zorunlu Kolon Kontrolü
    req_cols = ["AT Zimmet Personel Adı", "Teslim Eden Personel", "Kargo Teslimat Kanalı"]
    for col in req_cols:
        if col not in df.columns:
            st.error(f"❌ Excel dosyasında '{col}' sütunu bulunamadı!")
            return None

    # Açıklama Sütununu Kontrol Et
    has_aciklama = "Açıklama" in df.columns

    # Mantıksal Gruplamalar
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

    # Personel Bazlı Özet Tablo
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
        
        # Teslimat kanalları yalnızca Başarılı Teslimatlar üzerinden hesaplanır
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

    return pd.DataFrame(summary)

# ==========================================
# KURYELER PERFORMANS PANELİ
# ==========================================
st.subheader("🏃‍♂️ Kurye Performans Paneli")

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            raw_df = pd.read_csv(uploaded_file)
        else:
            raw_df = pd.read_excel(uploaded_file)
        
        perf_df = process_excel_data(raw_df)
    except Exception as e:
        st.error(f"Excel okunurken bir hata oluştu: {e}")
        perf_df = None
else:
    st.info("💡 Lütfen verilerin hesaplanması için sol menüden **AT ZİMMET İZLEME** Excel dosyasını yükleyin.")
    # Varsayılan Önizleme Verisi
    perf_df = pd.DataFrame([
        {"Personel": "AHMET BERKANT ÖKSÜZ", "Zimmet": 150, "Teslim Edilen": 142, "Teslim Edilemeyen": 8, "Başarı Oranı": 94.7, "SMS": 100, "İmza": 30, "KS-PE": 12},
        {"Personel": "MEHMET YILMAZ", "Zimmet": 120, "Teslim Edilen": 100, "Teslim Edilemeyen": 20, "Başarı Oranı": 83.3, "SMS": 70, "İmza": 20, "KS-PE": 10}
    ])

if perf_df is not None and not perf_df.empty:
    
    # Personelleri Alt Alta Listele
    for _, row in perf_df.iterrows():
        p_name = row["Personel"]
        zimmet = row["Zimmet"]
        teslim = row["Teslim Edilen"]
        devir = row["Teslim Edilemeyen"]
        rate = row["Başarı Oranı"]
        sms = row["SMS"]
        imza = row["İmza"]
        ks_pe = row["KS-PE"]
        
        svg_chart = generate_pie_svg(rate)
        avatar_url = f"https://ui-avatars.com/api/?name={p_name.replace(' ', '+')}&background=0B172E&color=F57C00&bold=true"

        card_html = f"""
        <div class="person-card">
            <!-- ÜST SATIR: RESİM, İSİM, ZİMMET, TESLİM, DEVİR, ÇEMBER GRAFİK -->
            <div class="person-main-row">
                <div class="profile-section">
                    <img src="{avatar_url}" class="avatar-circle" alt="{p_name}">
                    <div class="person-name">{p_name}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">Zimmet Sayısı</div>
                    <div class="metric-value" style="color: #FFFFFF;">{zimmet}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">Teslim Edilen</div>
                    <div class="metric-value" style="color: #4CAF50;">{teslim}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">Teslim Edilemeyen</div>
                    <div class="metric-value" style="color: #F44336;">{devir}</div>
                </div>
                <div class="chart-container">
                    {svg_chart}
                    <div class="chart-label">%{rate}</div>
                </div>
            </div>
            
            <!-- ALT SATIR: KARGO TESLİMAT KANALLARI -->
            <div class="channel-row">
                <div class="channel-badge">
                    <span>📲 SMS:</span>
                    <span class="badge-value">{sms}</span>
                </div>
                <div class="channel-badge">
                    <span>✍️ İMZA:</span>
                    <span class="badge-value">{imza}</span>
                </div>
                <div class="channel-badge">
                    <span>🚪 KS-PE:</span>
                    <span class="badge-value">{ks_pe}</span>
                </div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
