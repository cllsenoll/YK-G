
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Şube Operasyonel Performans Paneli",
    page_icon="📦",
    layout="wide"
)

# --- VERİ SETİ (KPOS Veri Yapısı) ---
@st.cache_data
def load_data():
    data = {
        "Kurye": ["Ahmet Yılmaz", "Mehmet Kaya", "Ayşe Demir", "Ali Can", "Fatma Şahin"],
        "Zimmet": [120, 140, 110, 95, 130],
        "Teslim": [112, 126, 105, 80, 104],
        "Devir": [8, 14, 5, 15, 26],
        "Sms": [80, 90, 75, 55, 70],
        "İmza": [32, 36, 30, 25, 34],
        "Nakit": [450.0, 600.0, 300.0, 200.0, 500.0],
        "Kart": [1200.0, 1500.0, 950.0, 800.0, 1100.0]
    }
    df = pd.DataFrame(data)
    # Teslimat Oranı Hesaplama (%)
    df["Teslimat_Orani"] = (df["Teslim"] / df["Zimmet"]) * 100
    return df

df = load_data()

# --- SEKME YAPISI ---
tab_main, tab_personel, tab_f4 = st.tabs([
    "📊 Ana Panel (Dashboard)", 
    "👤 Personel Hesap Alımı", 
    "💳 F4 Ödeme Listesi"
])

# ==========================================
# 1. ANA PANEL (DASHBOARD)
# ==========================================
with tab_main:
    st.title("📦 Şube Operasyonel Performans Paneli")
    st.markdown("---")

    # Toplam Veri Hesaplamaları
    toplam_zimmet = int(df["Zimmet"].sum())
    toplam_teslimat = int(df["Teslim"].sum())
    toplam_devir = int(df["Devir"].sum())
    
    # Günün Personeli (En yüksek teslimat oranına sahip kurye)
    gunun_personeli_row = df.loc[df["Teslimat_Orani"].idxmax()]
    gunun_personeli_ad = gunun_personeli_row["Kurye"]
    gunun_personeli_oran = gunun_personeli_row["Teslimat_Orani"]

    # 1. EN ÜST 4 KUTU (KPI METRİKLERİ)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="📦 Toplam Zimmet Sayısı", value=f"{toplam_zimmet:,}")

    with col2:
        st.metric(label="✅ Toplam Teslimat Sayısı", value=f"{toplam_teslimat:,}")

    with col3:
        st.metric(label="🔄 Devir Sayısı", value=f"{toplam_devir:,}")

    with col4:
        st.metric(
            label="🏆 Günün Personeli", 
            value=gunun_personeli_ad, 
            delta=f"%{gunun_personeli_oran:.1f} Başarı"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. ŞUBE PERFORMANSI (İBRE) VE KANALLAR (PASTA GRAFİĞİ) YAN YANA
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("🎯 Şube Genel Teslimat Performansı")
        genel_basari_orani = (toplam_teslimat / toplam_zimmet) * 100 if toplam_zimmet > 0 else 0
        
        # İbre (Gauge) Grafiği
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=genel_basari_orani,
            number={'suffix': "%", 'font': {'size': 36}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#1E88E5"},
                'steps': [
                    {'range': [0, 60], 'color': "#FFCDD2"},
                    {'range': [60, 85], 'color': "#FFE082"},
                    {'range': [85, 100], 'color': "#C8E6C9"}
                ],
                'threshold': {
                    'line': {'color': "green", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with chart_col2:
        st.subheader("🥧 Kargo Teslimat Kanalları Dağılımı")
        toplam_sms = int(df["Sms"].sum())
        toplam_imza = int(df["İmza"].sum())
        
        # Pasta / Donut Grafiği
        fig_pie = px.pie(
            names=["SMS ile Teslimat", "İmza / Adrese Teslimat"],
            values=[toplam_sms, toplam_imza],
            hole=0.4,
            color_discrete_sequence=["#26A69A", "#FFA726"]
        )
        fig_pie.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # 3. PERSONEL BAZLI KARŞILAŞTIRMALI TESLİMAT GRAFİĞİ VE LİSTESİ
    st.subheader("👥 Personel Bazlı Karşılaştırmalı Teslimat İstatistikleri")

    for idx, row in df.iterrows():
        with st.container():
            c_avatar, c_info, c_metrics, c_chart = st.columns([0.8, 2.2, 3.5, 2.5])
            
            with c_avatar:
                st.image(f"https://api.dicebear.com/7.x/bottts/svg?seed={row['Kurye']}", width=65)

            with c_info:
                st.markdown(f"### {row['Kurye']}")
                st.caption("Saha Kurye Personeli")

            with c_metrics:
                m1, m2, m3 = st.columns(3)
                m1.metric("Zimmet", row["Zimmet"])
                m2.metric("Teslim", row["Teslim"])
                m3.metric("Devir", row["Devir"])

            with c_chart:
                fig_ring = go.Figure(go.Pie(
                    values=[row["Teslimat_Orani"], max(0, 100 - row["Teslimat_Orani"])],
                    hole=0.7,
                    marker_colors=['#4CAF50', '#E0E0E0'],
                    textinfo='none',
                    hoverinfo='label+percent'
                ))
                fig_ring.update_layout(
                    showlegend=False,
                    height=90,
                    width=90,
                    margin=dict(l=0, r=0, t=0, b=0),
                    annotations=[dict(
                        text=f"%{row['Teslimat_Orani']:.0f}",
                        x=0.5, y=0.5,
                        font_size=16,
                        showarrow=False
                    )]
                )
                st.plotly_chart(fig_ring, use_container_width=False)
            
            st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

# ==========================================
# 2. PERSONEL HESAP ALIMI EKRANI
# ==========================================
with tab_personel:
    st.header("👤 Personel Hesap Alımı Ekranı")
    st.write("Personel hesap kapama işlemleri ve saha tahsilat verileri.")
    st.dataframe(df[["Kurye", "Zimmet", "Teslim", "Devir", "Nakit", "Kart"]], use_container_width=True)

# ==========================================
# 3. F4 ÖDEME LİSTESİ EKRANI
# ==========================================
with tab_f4:
    st.header("💳 F4 Ödeme Listesi Ekranı")
    st.write("Günlük nakit ve POS kart tahsilat listesi düzenlemeleri.")
    
    toplam_nakit = df["Nakit"].sum()
    toplam_kart = df["Kart"].sum()
    
    f4_col1, f4_col2 = st.columns(2)
    f4_col1.metric("💵 Toplam Nakit Tahsilat", f"{toplam_nakit:,.2f} TL")
    f4_col2.metric("💳 Toplam POS/Kart Tahsilat", f"{toplam_kart:,.2f} TL")
    
    st.dataframe(df[["Kurye", "Nakit", "Kart"]], use_container_width=True)
