import streamlit as st
import plotly.graph_objects as go

# Sayfa Ayarları
st.set_page_config(
    page_title="Ana Panel - Kargo Operasyon",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- BİREBİR TEMA VE KOLAJ CSS STİLLERİ ---
custom_css = """
<style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #070E1E;
        color: #FFFFFF;
    }
    
    /* Üst Başlıklar ve Yazılar */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #FFFFFF !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 1. TURUNCU KART (En Üst - AT Zimmet) */
    .kpi-card-orange {
        background: linear-gradient(135deg, #E65100 0%, #F57C00 100%);
        border-radius: 18px;
        padding: 16px 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(245, 124, 0, 0.25);
        margin-bottom: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* 2. MAVİ KARTLAR (Orta Satır Yan Yana - Teslim Edildi / Teslim Edilemedi) */
    .kpi-card-blue {
        background: linear-gradient(135deg, #0A43A6 0%, #032057 100%);
        border-radius: 18px;
        padding: 16px 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(10, 67, 166, 0.25);
        margin-bottom: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* 3. BEYAZ KART (En Alt - Günün Personeli) */
    .kpi-card-white {
        background: linear-gradient(135deg, #FFFFFF 0%, #E0E6ED 100%);
        border-radius: 18px;
        padding: 16px 20px;
        color: #070E1E !important;
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.15);
        margin-bottom: 15px;
        border: 1px solid #FFFFFF;
    }

    /* Kart Üst Başlık Düzeni */
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

    /* Kart Değer Yazıları */
    .kpi-value-dark {
        font-size: 24px;
        font-weight: 700;
        color: #FFFFFF !important;
        letter-spacing: 0.5px;
    }

    .kpi-value-light {
        font-size: 24px;
        font-weight: 800;
        color: #070E1E !important;
        letter-spacing: 0.5px;
    }

    /* Sidebar Gizleme */
    [data-testid="stSidebar"] {
        background-color: #091325;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# ==========================================
# İKON VE METRİK ŞABLON TANIMLARI (UI CONFIG)
# ==========================================

# 1x2x1 KOLAJ ŞABLONU
COLLAGE_CARDS = {
    # 1. EN ÜST SATIR (1 Tane Turuncu Kart)
    "top_single": {
        "title": "AT Zimmet",
        "left_icon": "📦",
        "right_icon": "⚙️",
        "value": "1.248",
        "style": "orange"
    },
    
    # 2. ORTA SATIR (2 Tane Mavi Kart - Yan Yana)
    "middle_left": {
        "title": "Teslim Edildi",
        "left_icon": "📝",
        "right_icon": "🚚",
        "value": "1.078",
        "style": "blue"
    },
    "middle_right": {
        "title": "Teslim Edilemedi",
        "left_icon": "🔄",
        "right_icon": "⚠️",
        "value": "170",
        "style": "blue"
    },
    
    # 3. EN ALT SATIR (1 Tane Beyaz Kart)
    "bottom_single": {
        "title": "Günün Personeli",
        "left_icon": "👑",
        "right_icon": "⭐",
        "value": "Ahmet Berkant Öksüz",  # En yüksek teslimatı yapan kurye buraya aktarılacak
        "style": "white"
    }
}

# GRAFİK ŞABLONU
CHART_CONFIG = {
    "title": "Teslimat Oranı",
    "percentage": 86.4,
    "legend_1_label": "Teslim Edilen",
    "legend_1_value": "1.078",
    "legend_1_color": "#0A58CA",
    "legend_2_label": "Teslim Edilemedi",
    "legend_2_value": "170",
    "legend_2_color": "#FF6B00"
}


# ==========================================
# ARAYÜZ OLUŞTURMA (LAYOUT)
# ==========================================

# Üst Başlık ve Tarih Seçici
col_title, col_date = st.columns([2, 1])
with col_title:
    st.subheader("☰ Ana Panel")

with col_date:
    st.date_input("", key="top_date_picker", label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------
# 1. EN ÜST SATIR (1 KART - TURUNCU: AT Zimmet)
# ------------------------------------------
card_top = COLLAGE_CARDS["top_single"]
st.markdown(f"""
    <div class="kpi-card-{card_top['style']}">
        <div class="kpi-header">
            <span class="kpi-title-dark">{card_top['left_icon']} {card_top['title']}</span>
            <span class="kpi-icon-right-dark">{card_top['right_icon']}</span>
        </div>
        <div class="kpi-value-dark">{card_top['value']}</div>
    </div>
""", unsafe_allow_html=True)


# ------------------------------------------
# 2. ORTA SATIR (2 KART YAN YANA - MAVİ: Teslim Edildi & Teslim Edilemedi)
# ------------------------------------------
mid_col1, mid_col2 = st.columns(2)

with mid_col1:
    card_m_left = COLLAGE_CARDS["middle_left"]
    st.markdown(f"""
        <div class="kpi-card-{card_m_left['style']}">
            <div class="kpi-header">
                <span class="kpi-title-dark">{card_m_left['left_icon']} {card_m_left['title']}</span>
                <span class="kpi-icon-right-dark">{card_m_left['right_icon']}</span>
            </div>
            <div class="kpi-value-dark">{card_m_left['value']}</div>
        </div>
    """, unsafe_allow_html=True)

with mid_col2:
    card_m_right = COLLAGE_CARDS["middle_right"]
    st.markdown(f"""
        <div class="kpi-card-{card_m_right['style']}">
            <div class="kpi-header">
                <span class="kpi-title-dark">{card_m_right['left_icon']} {card_m_right['title']}</span>
                <span class="kpi-icon-right-dark">{card_m_right['right_icon']}</span>
            </div>
            <div class="kpi-value-dark">{card_m_right['value']}</div>
        </div>
    """, unsafe_allow_html=True)


# ------------------------------------------
# 3. EN ALT SATIR (1 KART - BEYAZ: Günün Personeli)
# ------------------------------------------
card_bot = COLLAGE_CARDS["bottom_single"]
st.markdown(f"""
    <div class="kpi-card-{card_bot['style']}">
        <div class="kpi-header">
            <span class="kpi-title-light">{card_bot['left_icon']} {card_bot['title']}</span>
            <span class="kpi-icon-right-light">{card_bot['right_icon']}</span>
        </div>
        <div class="kpi-value-light">{card_bot['value']}</div>
    </div>
""", unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------
# TESLİMAT ORANI GRAFİĞİ
# ------------------------------------------
st.markdown(f"#### {CHART_CONFIG['title']}")

fig_donut = go.Figure(data=[go.Pie(
    labels=[CHART_CONFIG["legend_1_label"], CHART_CONFIG["legend_2_label"]],
    values=[float(CHART_CONFIG["legend_1_value"].replace('.', '')), float(CHART_CONFIG["legend_2_value"].replace('.', ''))],
    hole=0.70,
    marker_colors=[CHART_CONFIG["legend_1_color"], CHART_CONFIG["legend_2_color"]],
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
        text=f"<b>%{CHART_CONFIG['percentage']}</b>",
        x=0.5, y=0.5,
        font_size=28,
        font_color="white",
        showarrow=False
    )]
)

st.plotly_chart(fig_donut, use_container_width=True)
