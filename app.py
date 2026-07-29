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


# --- CSS ÖZELLEŞTİRMELERİ ---
custom_css = """
<style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #070E1E;
        color: #FFFFFF;
    }
    
    /* Genel Yazı Renkleri */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #FFFFFF !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Sol Yan Menü (Sidebar) Arka Planı */
    [data-testid="stSidebar"] {
        background-color: #0B172E !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* SOL MENÜDEKİ TÜM BUTONLAR İÇİN GENEL TEMEL */
    [data-testid="stSidebar"] button {
        width: 100% !important;
        height: 52px !important;
        min-height: 52px !important;
        border-radius: 12px !important;
        padding: 0 16px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        margin-bottom: 8px !important;
        border: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        transition: transform 0.15s ease, filter 0.15s ease !important;
    }

    /* 1. BUTON: ANA PANEL -> Yurtiçi Laciverti */
    [data-testid="stSidebar"] div.stElementContainer:has(button[key="btn_ana"]) button {
        background: linear-gradient(135deg, #0B2545 0%, #134074 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 4px 10px rgba(11, 37, 69, 0.5) !important;
    }

    /* 2. BUTON: KURYE PERFORMANS -> Yurtiçi Laciverti */
    [data-testid="stSidebar"] div.stElementContainer:has(button[key="btn_kurye"]) button {
        background: linear-gradient(135deg, #0B2545 0%, #134074 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 4px 10px rgba(11, 37, 69, 0.5) !important;
    }

    /* 3. BUTON: SEKRETER HESAP -> TURUNCU (Yurtiçi Sarısı/Turuncusu) */
    [data-testid="stSidebar"] div.stElementContainer:has(button[key="btn_sekreter"]) button {
        background: linear-gradient(135deg, #FF6B00 0%, #FF8800 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 4px 10px rgba(255, 107, 0, 0.4) !important;
    }
    
    /* Turuncu Buton Üzerindeki Metin Rengi */
    [data-testid="stSidebar"] div.stElementContainer:has(button[key="btn_sekreter"]) button p,
    [data-testid="stSidebar"] div.stElementContainer:has(button[key="btn_sekreter"]) button span {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* 4. BUTON: F4 ÖDEME LİSTESİ -> Yurtiçi Laciverti */
    [data-testid="stSidebar"] div.stElementContainer:has(button[key="btn_f4"]) button {
        background: linear-gradient(135deg, #0B2545 0%, #134074 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 4px 10px rgba(11, 37, 69, 0.5) !important;
    }

    /* HOVER DURUMU */
    [data-testid="stSidebar"] button:hover {
        transform: translateY(-2px) !important;
        filter: brightness(1.15) !important;
    }

    /* KPI KARTLARI STİLLERİ */
    .kpi-card-orange {
        background: linear-gradient(135deg, #FF6B00 0%, #FF8800 100%);
        border-radius: 18px;
        padding: 16px 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(255, 107, 0, 0.25);
        margin-bottom: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
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
        border-radius: 18px;
        padding: 16px 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(11, 37, 69, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.08);
        min-width: 0;
    }

    .kpi-card-white {
        background: #FFFFFF;
        border-radius: 18px;
        padding: 16px 20px;
        color: #0B2545 !important;
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.15);
        margin-bottom: 15px;
        border: 1px solid #FFFFFF;
    }

    .kpi-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }

    .kpi-title-dark {
        font-size: 13px;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.9) !important;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .kpi-title-light {
        font-size: 13px;
        font-weight: 700;
        color: #0B2545 !important;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .kpi-icon-right-dark {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 50%;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
    }

    .kpi-icon-right-light {
        background: rgba(11, 37, 69, 0.1);
        border-radius: 50%;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
    }

    .kpi-value-dark {
        font-size: 24px;
        font-weight: 700;
        color: #FFFFFF !important;
    }

    .kpi-value-light {
        font-size: 24px;
        font-weight: 800;
        color: #0B2545 !important;
    }

    /* PROFİL KARTI STİLİ */
    .user-profile-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 12px 14px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 40px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    .user-profile-img {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #FF6B00;
    }

    .user-info-name {
        font-size: 15px;
        font-weight: 700;
        color: #FFFFFF !important;
        line-height: 1.2;
    }

    .user-info-role {
        font-size: 12px;
        color: #FF6B00 !important;
        font-weight: 600;
        margin-top: 3px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# ==========================================
# SOL TARAF AÇILIR MENÜ (SIDEBAR)
# ==========================================
with st.sidebar:
    # 1. MENÜ BAŞLIĞI
    st.markdown("<h3 style='margin-bottom:4px; padding-top:10px;'>Yurtiçi Kargo</h3><h5 style='color:#FF6B00 !important; margin-top:0;'>Görükle Acente</h5>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin-top:8px; margin-bottom:18px;'>", unsafe_allow_html=True)
    
    # 2. SEKMELER
    if st.button("📊 Ana Panel", key="btn_ana"):
        st.session_state.active_tab = "Ana Panel"

    if st.button("🏃‍♂️ Kurye Performans", key="btn_kurye"):
        st.session_state.active_tab = "Kurye Performans"

    if st.button("💼 Sekreter Hesap", key="btn_sekreter"):
        st.session_state.active_tab = "Sekreter Hesap"

    if st.button("💳 F4 Ödeme Listesi", key="btn_f4"):
        st.session_state.active_tab = "F4 Ödeme Listesi"

    # 3. PROFİL KARTI
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
# SAYFA BAŞLIĞI VE TARİH FİLTRESİ
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
            <div class="kpi-header">
                <span class="kpi-title-dark">📦 AT Zimmet</span>
                <span class="kpi-icon-right-dark">⚙️</span>
            </div>
            <div class="kpi-value-dark">1.248</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="blue-cards-row">
            <div class="kpi-card-blue">
                <div class="kpi-header">
                    <span class="kpi-title-dark">📝 Teslim Edildi</span>
                    <span class="kpi-icon-right-dark">🚚</span>
                </div>
                <div class="kpi-value-dark">1.078</div>
            </div>
            <div class="kpi-card-blue">
                <div class="kpi-header">
                    <span class="kpi-title-dark">🔄 Teslim Edilemedi</span>
                    <span class="kpi-icon-right-dark">⚠️</span>
                </div>
                <div class="kpi-value-dark">170</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="kpi-card-white">
            <div class="kpi-header">
                <span class="kpi-title-light">👑 Günün Personeli</span>
                <span class="kpi-icon-right-light">⭐</span>
            </div>
            <div class="kpi-value-light">{KULLANICI_ISIM} ({KULLANICI_GOREV})</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Teslimat Oranı")
    fig_donut = go.Figure(data=[go.Pie(
        labels=["Teslim Edilen", "Teslim Edilemedi"],
        values=[1078, 170],
        hole=0.70,
        marker_colors=["#0B2545", "#FF6B00"],
        textinfo="none"
    )])

    fig_donut.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"),
        showlegend=True,
        height=240,
        margin=dict(l=10, r=10, t=10, b=10),
        annotations=[dict(
            text="<b>%86.4</b>",
            x=0.5, y=0.5,
            font_size=28,
            font_color="white",
            showarrow=False
        )]
    )
    st.plotly_chart(fig_donut, use_container_width=True)


elif st.session_state.active_tab == "Kurye Performans":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="kpi-card-blue">
                <div class="kpi-title-dark">🏃 Sahadaki Kurye</div>
                <div class="kpi-value-dark">14 Personel</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="kpi-card-orange">
                <div class="kpi-title-dark">⚡ Sorumlu Şef</div>
                <div class="kpi-value-dark">{KULLANICI_ISIM}</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="kpi-card-blue">
                <div class="kpi-title-dark">🎯 Ort. Başarı</div>
                <div class="kpi-value-dark">%91.2</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🏆 Kurye Performans Tablosu")
    
    kurye_data = pd.DataFrame({
        "Kurye Adı": ["Ahmet Berkant Öksüz", "Mehmet Yılmaz", "Ali Kaya", "Caner Erkin", "Burak Yılmaz"],
        "Zimmet Sayısı": [150, 130, 125, 110, 95],
        "Teslim Edilen": [142, 120, 110, 98, 80],
        "Kalan / İade": [8, 10, 15, 12, 15],
        "Başarı Oranı (%)": ["%94.6", "%92.3", "%88.0", "%89.0", "%84.2"],
        "Durum": ["🟢 Harika", "🟢 İyi", "🟡 Orta", "🟢 İyi", "🔴 Riskli"]
    })
    st.dataframe(kurye_data, use_container_width=True, hide_index=True)


elif st.session_state.active_tab == "Sekreter Hesap":
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div class="kpi-card-orange">
                <div class="kpi-title-dark">💵 Günlük Nakit Tahsilat</div>
                <div class="kpi-value-dark">₺ 14.850,00</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="kpi-card-blue">
                <div class="kpi-title-dark">💳 POS / Kredi Kartı Tahsilat</div>
                <div class="kpi-value-dark">₺ 32.410,50</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("### 💼 Kasa Hareketleri ve Muhasebe Özeti")
    
    hesap_data = pd.DataFrame({
        "Saat": ["09:15", "10:30", "11:45", "13:20", "15:10"],
        "İşlem Tipi": ["Nakit Tahsilat", "POS Tahsilat", "Kurye Avans", "Nakit Tahsilat", "POS Tahsilat"],
        "Açıklama": ["Şube Alıcı Ödemeli", "Kurye Gün Sonu", "Yakıt Ödemesi", "Şube Teslimat", "Saha Tahsilatı"],
        "Tutar": ["₺ 1.250", "₺ 8.400", "-₺ 500", "₺ 3.100", "₺ 12.150"],
        "Onaylayan Şef": [KULLANICI_ISIM, KULLANICI_ISIM, KULLANICI_ISIM, KULLANICI_ISIM, KULLANICI_ISIM]
    })
    st.dataframe(hesap_data, use_container_width=True, hide_index=True)


elif st.session_state.active_tab == "F4 Ödeme Listesi":
    st.markdown("""
        <div class="kpi-card-white">
            <div class="kpi-header">
                <span class="kpi-title-light">💳 Bekleyen F4 Tahsilat & Ödemeler</span>
                <span class="kpi-icon-right-light">💰</span>
            </div>
            <div class="kpi-value-light">₺ 18.650,00 (48 Kargo)</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 💳 F4 Ödeme ve Tahsilat Takip Listesi")
    
    f4_data = pd.DataFrame({
        "Takip No": ["TR8912341", "TR8912342", "TR8912343", "TR8912344", "TR8912345"],
        "Müşteri / Alıcı": ["Tekno A.Ş.", "Mustafa Demir", "Aysun Çelik", "Kaya Lojistik", "Elif Şahin"],
        "Ödeme Tipi": ["Gönderici Ödemeli", "Alıcı Ödemeli", "Kapıda Ödeme", "Alıcı Ödemeli", "Kapıda Ödeme"],
        "Tutar": ["₺ 450,00", "₺ 1.200,00", "₺ 850,00", "₺ 3.400,00", "₺ 620,00"],
        "Ödeme Durumu": ["🟡 Bekliyor", "🟢 Tahsil Edildi", "🔴 Problem/İade", "🟡 Bekliyor", "🟢 Tahsil Edildi"]
    })
    st.dataframe(f4_data, use_container_width=True, hide_index=True)
