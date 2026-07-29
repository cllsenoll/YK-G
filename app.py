import streamlit as st
import plotly.graph_objects as go

# Sayfa Ayarları
st.set_page_config(
    page_title="Ana Panel - Kargo Operasyon",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- BİREBİR TEMA CSS STİLLERİ ---
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

    /* KPI Kart Konteyner Yapısı */
    .kpi-card-blue {
        background: linear-gradient(135deg, #0A43A6 0%, #032057 100%);
        border-radius: 18px;
        padding: 18px 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .kpi-card-orange {
        background: linear-gradient(135deg, #E65100 0%, #F57C00 100%);
        border-radius: 18px;
        padding: 18px 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    /* Kart Üst Başlık ve İkon Alanı */
    .kpi-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .kpi-title {
        font-size: 13px;
        font-weight: 500;
        opacity: 0.9;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .kpi-icon-right {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 50%;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
    }

    /* Kart Değer Alanı */
    .kpi-value {
        font-size: 22px;
        font-weight: 700;
        letter-spacing: 0.5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
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

# 1. KART ŞABLONLARI (2 Üst + 2 Alt Düzeni)
METRIC_CARDS = {
    # --- ÜST SATIR ---
    "top_left": {
        "title": "Zimmet",
        "left_icon": "📦",
        "right_icon": "⚙️",
        "value": "1.248",
        "type": "blue"
    },
    "top_right": {
        "title": "Teslim Edilen",
        "left_icon": "📝",
        "right_icon": "🚚",
        "value": "1.078",
        "type": "orange"
    },
    # --- ALT SATIR ---
    "bottom_left": {
        "title": "Devir",
        "left_icon": "🔄",
        "right_icon": "🔁",
        "value": "170",
        "type": "blue"
    },
    "bottom_right": {
        "title": "Günün Personeli",
        "left_icon": "👑",
        "right_icon": "⭐",
        "value": "Ahmet Berkant",  # Buraya veri bağlandığında en yüksek teslimat yapan personel adı gelecek
        "type": "orange"
    }
}

# 2. GRAFİK ŞABLONU
CHART_CONFIG = {
    "title": "Teslimat Oranı",
    "percentage": 86.4,
    "legend_1_label": "Teslim Edilen",
    "legend_1_value": "1.078",
    "legend_1_color": "#0A58CA",
    "legend_2_label": "Devir",
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
# KARTLAR SATIR 1 (ÜST: Zimmet | Teslim Edilen)
# ------------------------------------------
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    card = METRIC_CARDS["top_left"]
    st.markdown(f"""
        <div class="kpi-card-{card['type']}">
            <div class="kpi-header">
                <span class="kpi-title">{card['left_icon']} {card['title']}</span>
                <span class="kpi-icon-right">{card['right_icon']}</span>
            </div>
            <div class="kpi-value">{card['value']}</div>
        </div>
    """, unsafe_allow_html=True)

with row1_col2:
    card = METRIC_CARDS["top_right"]
    st.markdown(f"""
        <div class="kpi-card-{card['type']}">
            <div class="kpi-header">
                <span class="kpi-title">{card['left_icon']} {card['title']}</span>
                <span class="kpi-icon-right">{card['right_icon']}</span>
            </div>
            <div class="kpi-value">{card['value']}</div>
        </div>
    """, unsafe_allow_html=True)

# ------------------------------------------
# KARTLAR SATIR 2 (ALT: Devir | Günün Personeli)
# ------------------------------------------
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    card = METRIC_CARDS["bottom_left"]
    st.markdown(f"""
        <div class="kpi-card-{card['type']}">
            <div class="kpi-header">
                <span class="kpi-title">{card['left_icon']} {card['title']}</span>
                <span class="kpi-icon-right">{card['right_icon']}</span>
            </div>
            <div class="kpi-value">{card['value']}</div>
        </div>
    """, unsafe_allow_html=True)

with row2_col2:
    card = METRIC_CARDS["bottom_right"]
    st.markdown(f"""
        <div class="kpi-card-{card['type']}">
            <div class="kpi-header">
                <span class="kpi-title">{card['left_icon']} {card['title']}</span>
                <span class="kpi-icon-right">{card['right_icon']}</span>
            </div>
            <div class="kpi-value">{card['value']}</div>
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
