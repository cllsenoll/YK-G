import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. Sayfa Ayarları (Sol Menü Açılabilir Halde)
st.set_page_config(
    page_title="Yurtiçi Kargo Görükle Acente",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. OTURUM DURUMU (Session State) - Seçili Sekmeyi Tutma
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Ana Panel"

# --- KULLANICI PROFİL BİLGİLERİ (İsteğinize göre düzenleyin) ---
KULLANICI_ISIM = "Ahmet Berkant Öksüz"
KULLANICI_GOREV = "Acente Yöneticisi"
# Fotoğrafınızın linkini veya 'profil.jpg' gibi dosya yolunu buraya yazabilirsiniz:
FOTO_URL = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"


# --- BİREBİR TEMA VE ÖZEL CSS STİLLERİ ---
custom_css = """
<style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #070E1E;
        color: #FFFFFF;
    }
    
    /* Üst Başlıklar ve Genel Yazılar */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #FFFFFF !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Sol Yan Menü (Sidebar) Stil Özelleştirme */
    [data-testid="stSidebar"] {
        background-color: #0B172E !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* MENÜ BUTONLARI - SIRASIYLA MAVİ VE TURUNCU STİLLER */
    
    /* Mavi Menü Butonu */
    div.stButton > button.nav-btn-blue {
        background: linear-gradient(135deg, #0A43A6 0%, #032057 100%) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        width: 100% !important;
        text-align: left !important;
        margin-bottom: 10px !important;
        box-shadow: 0 4px 12px rgba(10, 67, 166, 0.3) !important;
    }

    /* Turuncu Menü Butonu */
    div.stButton > button.nav-btn-orange {
        background: linear-gradient(135deg, #E65100 0%, #F57C00 100%) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        width: 100% !important;
        text-align: left !important;
        margin-bottom: 10px !important;
        box-shadow: 0 4px 12px rgba(245, 124, 0, 0.3) !important;
    }

    /* KPI KARTLARI STİLLERİ */
    .kpi-card-orange {
        background: linear-gradient(135deg, #E65100 0%, #F57C00 100%);
        border-radius: 18px;
        padding: 16px 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(245, 124, 0, 0.25);
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
        background: linear-gradient(135deg, #0A43A6 0%, #032057 100%);
        border-radius: 18px;
        padding: 16px 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(10, 67, 166, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.08);
        min-width: 0;
    }

    .kpi-card-white {
        background: linear-gradient(135deg, #FFFFFF 0%, #E0E6ED 100%);
        border-radius: 18px;
        padding: 16px 20px;
        color: #070E1E !important;
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
        color: #070E1E !important;
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
        background: rgba(7, 14, 30, 0.1);
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
        color: #070E1E !important;
    }

    /* PROFİL KARTI STİLİ (SOL MENÜ EN ALT) */
    .user-profile-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 12px 14px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 30px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    .user-profile-img {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #F57C00;
    }

    .user-info-name {
        font-size: 14px;
        font-weight: 700;
        color: #FFFFFF !important;
        line-height: 1.2;
    }

    .user-info-role {
        font-size: 12px;
        color: #F57C00 !important;
        font-weight: 600;
        margin-top: 2px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# ==========================================
# SOL TARAF AÇILIR MENÜ (SIDEBAR)
# ==========================================
with st.sidebar:
    # 1. MENÜ BAŞLIĞI
    st.markdown("### 🚚 Yurtiçi Kargo<br>Görükle Acente", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin-top:8px; margin-bottom:18px;'>", unsafe_allow_html=True)
    
    # 2. SEKMELER (Sırasıyla Mavi ve Turuncu)
    # Sekme 1: Ana Panel (Mavi)
    btn_ana = st.button("📊 Ana Panel", key="btn_ana")
    if btn_ana:
        st.session_state.active_tab = "Ana Panel"

    # Sekme 2: Kurye Performans (Turuncu)
    btn_kurye = st.button("🏃‍♂️ Kurye Performans", key="btn_kurye")
    if btn_kurye:
        st.session_state.active_tab = "Kurye Performans"

    # Sekme 3: Sekreter Hesap (Mavi)
    btn_sekreter = st.button("💼 Sekreter Hesap", key="btn_sekreter")
    if btn_sekreter:
        st.session_state.active_tab = "Sekreter Hesap"

    # Sekme 4: F4 Listesi (Turuncu)
    btn_f4 = st.button("📋 F4 Listesi", key="btn_f4")
    if btn_f4:
        st.session_state.active_tab = "F4 Listesi"

    # 3. EN ALT PROFİL KARINI OLUŞTURMA
    st.markdown(f"""
        <div class="user-profile-card">
            <img src="{FOTO_URL}" class="user-profile-img" alt="Profil Fotoğrafı">
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
# EKRAN İÇERİKLERİ (SEKMELERE GÖRE DİNAMİK)
# ==========================================

# ------------------------------------------
# EKRAN 1: ANA PANEL
# ------------------------------------------
if st.session_state.active_tab == "Ana Panel":
    
    # KPI 1: AT Zimmet (Turuncu Kart)
    st.markdown("""
        <div class="kpi-card-orange">
            <div class="kpi-header">
                <span class="kpi-title-dark">📦 AT Zimmet</span>
                <span class="kpi-icon-right-dark">⚙️</span>
            </div>
            <div class="kpi-value-dark">1.248</div>
        </div>
    """, unsafe_allow_html=True)

    # KPI 2 & 3: Teslim Edildi / Edilemedi (Yan Yana Mavi Kartlar)
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

    # KPI 4: Günün Personeli (Beyaz Kart)
    st.markdown(f"""
        <div class="kpi-card-white">
            <div class="kpi-header">
                <span class="kpi-title-light">👑 Günün Personeli</span>
                <span class="kpi-icon-right-light">⭐</span>
            </div>
            <div class="kpi-value-light">{KULLANICI_ISIM}</div>
        </div>
    """, unsafe_allow_html=True)

    # Grafik
    st.markdown("#### Teslimat Oranı")
    fig_donut = go.Figure(data=[go.Pie(
        labels=["Teslim Edilen", "Teslim Edilemedi"],
        values=[1078, 170],
        hole=0.70,
        marker_colors=["#0A58CA", "#FF6B00"],
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


# ------------------------------------------
# EKRAN 2: KURYE PERFORMANS
# ------------------------------------------
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
                <div class="kpi-title-dark">⚡ En Hızlı Kurye</div>
                <div class="kpi-value-dark">{KULLANICI_ISIM} (142)</div>
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
        "Kurye Adı": [KULLANICI_ISIM, "Mehmet Yılmaz", "Ali Kaya", "Caner Erkin", "Burak Yılmaz"],
        "Zimmet Sayısı": [150, 130, 125, 110, 95],
        "Teslim Edilen": [142, 120, 110, 98, 80],
        "Kalan / İade": [8, 10, 15, 12, 15],
        "Başarı Oranı (%)": ["%94.6", "%92.3", "%88.0", "%89.0", "%84.2"],
        "Durum": ["🟢 Harika", "🟢 İyi", "🟡 Orta", "🟢 İyi", "🔴 Riskli"]
    })
    
    st.dataframe(kurye_data, use_container_width=True, hide_index=True)


# ------------------------------------------
# EKRAN 3: SEKRETER HESAP
# ------------------------------------------
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
        "İşlemi Yapan": ["Seda A.", KULLANICI_ISIM, "Mehmet Y.", "Seda A.", "Ali K."]
    })
    
    st.dataframe(hesap_data, use_container_width=True, hide_index=True)


# ------------------------------------------
# EKRAN 4: F4 LİSTESİ
# ------------------------------------------
elif st.session_state.active_tab == "F4 Listesi":
    
    st.markdown("""
        <div class="kpi-card-white">
            <div class="kpi-header">
                <span class="kpi-title-light">📋 Toplam F4 Bekleyen Kargolar</span>
                <span class="kpi-icon-right-light">📦</span>
            </div>
            <div class="kpi-value-light">48 Adet Kargo</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔍 F4 Zimmet İade ve Problem Listesi")
    
    f4_data = pd.DataFrame({
        "Takip No": ["TR8912341", "TR8912342", "TR8912343", "TR8912344", "TR8912345"],
        "Alıcı Adı": ["Tekno A.Ş.", "Mustafa Demir", "Aysun Çelik", "Kaya Lojistik", "Elif Şahin"],
        "Sebep / Problem": ["Adreste Yok / Haber Kağıdı", "Hatalı Adres", "Müşteri Kabul Etmiyor", "Randevulu Teslimat", "Telefon Ulaşılamıyor"],
        "Sorumlu Kurye": ["Mehmet Y.", "Ali K.", "Caner E.", KULLANICI_ISIM, "Burak Y."],
        "Aksiyon": ["Yarın Tekrar Çıkacak", "Adres Teyidi Bekliyor", "İade Oluşturuldu", "Beklemede", "SMS Gönderildi"]
    })
    
    st.dataframe(f4_data, use_container_width=True, hide_index=True)
