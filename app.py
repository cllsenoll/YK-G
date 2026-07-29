import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. Sayfa Ayarları
st.set_page_config(
    page_title="Yurtiçi Kargo Görükle Acente",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. OTURUM DURUMU (Session State)
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Ana Panel"

# --- KULLANICI PROFİL BİLGİLERİ ---
KULLANICI_ISIM = "Celal Şenol"
KULLANICI_GOREV = "Şube Şefi"
FOTO_URL = "celal_senol.jpg" 


# --- CSS ÖZELLEŞTİRMELERİ (Garanti Stil Enjeksiyonu) ---
custom_css = """
<style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #070E1E;
        color: #FFFFFF;
    }
    
    /* Sol Yan Menü (Sidebar) Arka Planı */
    [data-testid="stSidebar"] {
        background-color: #0B172E !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* SIDEBAR İÇİNDEKİ TÜM BUTONLARIN ORTAK EBATLARI */
    [data-testid="stSidebar"] button {
        width: 100% !important;
        height: 52px !important;
        min-height: 52px !important;
        border-radius: 10px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        margin-bottom: 8px !important;
        border: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        padding-left: 16px !important;
        transition: transform 0.15s ease, filter 0.15s ease !important;
    }

    /* 1. BUTON - ANA PANEL (Yurtiçi Laciverti) */
    [data-testid="stSidebar"] div.stElementContainer:has(button[key="btn_ana"]) button {
        background: linear-gradient(135deg, #0B2545 0%, #134074 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 4px 10px rgba(11, 37, 69, 0.5) !important;
    }

    /* 2. BUTON - KURYE PERFORMANS (Yurtiçi Turuncusu/Sarısı) */
    [data-testid="stSidebar"] div.stElementContainer:has(button[key="btn_kurye"]) button {
        background: linear-gradient(135deg, #FF6B00 0%, #FF8800 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 4px 10px rgba(255, 107, 0, 0.4) !important;
    }

    /* 3. BUTON - SEKRETER HESAP (Temiz Beyaz) */
    [data-testid="stSidebar"] div.stElementContainer:has(button[key="btn_sekreter"]) button {
        background: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
        box-shadow: 0 4px 10px rgba(255, 255, 255, 0.2) !important;
    }

    /* Beyaz Buton İçi Yazı Rengi */
    [data-testid="stSidebar"] div.stElementContainer:has(button[key="btn_sekreter"]) button p,
    [data-testid="stSidebar"] div.stElementContainer:has(button[key="btn_sekreter"]) button span {
        color: #0B2545 !important;
        font-weight: 800 !important;
    }

    /* 4. BUTON - F4 ÖDEME LİSTESİ (Yurtiçi Laciverti) */
    [data-testid="stSidebar"] div.stElementContainer:has(button[key="btn_f4"]) button {
        background: linear-gradient(135deg, #0B2545 0%, #134074 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 4px 10px rgba(11, 37, 69, 0.5) !important;
    }

    /* HOVER VE EFFECT */
    [data-testid="stSidebar"] button:hover {
        transform: scale(1.02) !important;
        filter: brightness(1.1) !important;
    }

    /* KPI KARTLARI */
    .kpi-card-orange {
        background: linear-gradient(135deg, #FF6B00 0%, #FF8800 100%);
        border-radius: 16px;
        padding: 16px 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(255, 107, 0, 0.25);
        margin-bottom: 12px;
    }

    .blue-cards-row {
        display: flex;
        gap: 12px;
        width: 100%;
        margin-bottom: 12px;
    }

    .kpi-card-blue {
        flex: 1;
        background: linear-gradient(135deg, #0B2545 0%, #134074 100%);
        border-radius: 16px;
        padding: 16px 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(11, 37, 69, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .kpi-card-white {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 16px 20px;
        color: #0B2545 !important;
        box-shadow: 0 4px 15px rgba(255, 255, 255, 0.15);
        margin-bottom: 15px;
    }

    .kpi-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }

    .kpi-title-dark { font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.9); }
    .kpi-title-light { font-size: 13px; font-weight: 700; color: #0B2545; }
    .kpi-value-dark { font-size: 24px; font-weight: 700; color: #FFFFFF; }
    .kpi-value-light { font-size: 24px; font-weight: 800; color: #0B2545; }

    /* PROFİL KARTI */
    .user-profile-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 10px 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 30px;
    }

    .user-profile-img {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #FF6B00;
    }

    .user-info-name { font-size: 14px; font-weight: 700; color: #FFFFFF; }
    .user-info-role { font-size: 12px; color: #FF6B00; font-weight: 600; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# ==========================================
# SOL TARAF AÇILIR MENÜ (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='margin-bottom:2px; padding-top:10px;'>Yurtiçi Kargo</h3><h5 style='color:#FF6B00 !important; margin-top:0;'>Görükle Acente</h5>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin-top:6px; margin-bottom:16px;'>", unsafe_allow_html=True)
    
    # BUTONLAR (Mavi - Turuncu - Beyaz - Mavi)
    if st.button("📊 Ana Panel", key="btn_ana"):
        st.session_state.active_tab = "Ana Panel"

    if st.button("🏃‍♂️ Kurye Performans", key="btn_kurye"):
        st.session_state.active_tab = "Kurye Performans"

    if st.button("💼 Sekreter Hesap", key="btn_sekreter"):
        st.session_state.active_tab = "Sekreter Hesap"

    if st.button("💳 F4 Ödeme Listesi", key="btn_f4"):
        st.session_state.active_tab = "F4 Ödeme Listesi"

    # PROFİL KARTI
    st.markdown(f"""
        <div class="user-profile-card">
            <img src="app/static/{FOTO_URL}" class="user-profile-img" alt="Celal Şenol" onerror="this.src='https://ui-avatars.com/api/?name=Celal+Senol&background=FF6B00&color=fff'">
            <div>
                <div class="user-info-name">{KULLANICI_ISIM}</div>
                <div class="user-info-role">{KULLANICI_GOREV}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


# ==========================================
# SAYFA BAŞLIĞI
# ==========================================
col_title, col_date = st.columns([2, 1])
with col_title:
    st.subheader(f"☰ {st.session_state.active_tab}")
with col_date:
    st.date_input("", key="top_date_picker", label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# EKRAN İÇERİKLERİ
# ==========================================
if st.session_state.active_tab == "Ana Panel":
    st.markdown("""
        <div class="kpi-card-orange">
            <div class="kpi-header"><span class="kpi-title-dark">📦 AT Zimmet</span></div>
            <div class="kpi-value-dark">1.248</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="blue-cards-row">
            <div class="kpi-card-blue">
                <div class="kpi-header"><span class="kpi-title-dark">📝 Teslim Edildi</span></div>
                <div class="kpi-value-dark">1.078</div>
            </div>
            <div class="kpi-card-blue">
                <div class="kpi-header"><span class="kpi-title-dark">🔄 Teslim Edilemedi</span></div>
                <div class="kpi-value-dark">170</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="kpi-card-white">
            <div class="kpi-header"><span class="kpi-title-light">👑 Günün Personeli</span></div>
            <div class="kpi-value-light">{KULLANICI_ISIM} ({KULLANICI_GOREV})</div>
        </div>
    """, unsafe_allow_html=True)

elif st.session_state.active_tab == "Kurye Performans":
    st.markdown("### 🏆 Kurye Performans Tablosu")
    kurye_data = pd.DataFrame({
        "Kurye Adı": ["Ahmet Berkant Öksüz", "Mehmet Yılmaz", "Ali Kaya"],
        "Zimmet Sayısı": [150, 130, 125],
        "Başarı Oranı (%)": ["%94.6", "%92.3", "%88.0"]
    })
    st.dataframe(kurye_data, use_container_width=True, hide_index=True)

elif st.session_state.active_tab == "Sekreter Hesap":
    st.markdown("### 💼 Kasa Hareketleri ve Muhasebe Özeti")
    hesap_data = pd.DataFrame({
        "Saat": ["09:15", "10:30"],
        "İşlem Tipi": ["Nakit Tahsilat", "POS Tahsilat"],
        "Tutar": ["₺ 1.250", "₺ 8.400"]
    })
    st.dataframe(hesap_data, use_container_width=True, hide_index=True)

elif st.session_state.active_tab == "F4 Ödeme Listesi":
    st.markdown("### 💳 F4 Ödeme ve Tahsilat Takip Listesi")
    f4_data = pd.DataFrame({
        "Takip No": ["TR8912341", "TR8912342"],
        "Müşteri": ["Tekno A.Ş.", "Mustafa Demir"],
        "Tutar": ["₺ 450,00", "₺ 1.200,00"]
    })
    st.dataframe(f4_data, use_container_width=True, hide_index=True)
