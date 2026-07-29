import streamlit as st
import pandas as pd
import io
import plotly.express as px
import plotly.graph_objects as go

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
        width: 58px;
        height: 58px;
        border-radius: 50%;
        border: 2px solid #F57C00;
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
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# TÜM YURTİÇİ KARGO DOSYA TÜRLERİNİ OKUYAN MOTOR
# ==========================================
def load_uploaded_file(uploaded_file):
    file_bytes = uploaded_file.getvalue()

    # 1. Türkçe Windows CSV (CP1254/ISO-8859-9 - Noktalı Virgül) -> F4 ÖDEME LİSTESİ dahil
    try:
        return pd.read_csv(io.BytesIO(file_bytes), sep=';', encoding='cp1254')
    except Exception:
        pass

    try:
        return pd.read_csv(io.BytesIO(file_bytes), sep=';', encoding='iso-8859-9')
    except Exception:
        pass

    # 2. HTML Tablosu Çıktıları (Sistem XLS raporları)
    try:
        dfs = pd.read_html(io.BytesIO(file_bytes), encoding='utf-8')
        if dfs and len(dfs) > 0:
            return dfs[0]
    except Exception:
        pass

    try:
        dfs = pd.read_html(io.BytesIO(file_bytes), encoding='latin1')
        if dfs and len(dfs) > 0:
            return dfs[0]
    except Exception:
        pass

    # 3. XLSX (OpenPyXL)
    try:
        return pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
    except Exception:
        pass

    # 4. XLS (XLRD)
    try:
        return pd.read_excel(io.BytesIO(file_bytes), engine='xlrd')
    except Exception:
        pass

    # 5. Standart UTF-8 CSV
    try:
        return pd.read_csv(io.BytesIO(file_bytes), sep=';', encoding='utf-8')
    except Exception:
        pass

    try:
        return pd.read_csv(io.BytesIO(file_bytes), encoding='utf-8')
    except Exception:
        pass

    raise ValueError("Dosya okunamadı. Lütfen geçerli bir Excel (.xlsx / .xls) veya CSV dosyası yükleyin.")

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

    return pd.DataFrame(summary), None

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

    uploaded_file = st.file_uploader("📂 Rapor / Liste Yükle", type=None)
    
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    if st.button("📊 Ana Panel"):
        st.session_state.active_tab = "Ana Panel"
    if st.button("🏃‍♂️ Kurye Performans"):
        st.session_state.active_tab = "Kurye Performans"
    if st.button("👩‍💼 Operatör Performans"):
        st.session_state.active_tab = "Operatör Performans"
    if st.button("📈 Genel Grafikler & Rapor"):
        st.session_state.active_tab = "Genel Raporlama"

# ==========================================
# VERİ YÜKLEME VE İŞLEME AŞAMASI
# ==========================================
perf_df = None
raw_df = None
missing_columns = None

if uploaded_file is not None:
    try:
        raw_df = load_uploaded_file(uploaded_file)
        perf_df, missing_columns = process_excel_data(raw_df)
    except Exception as e:
        st.error(f"❌ Dosya Okuma Hatası: {e}")

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
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("📊 Kurye Başarı Oranları (%)")
            fig_bar = px.bar(
                perf_df, 
                x="Personel", 
                y="Başarı Oranı", 
                color="Başarı Oranı",
                color_continuous_scale="RdYlGn",
                text="Başarı Oranı"
            )
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_right:
            st.subheader("📲 Teslimat Kanalları Dağılımı")
            channel_totals = {
                "SMS": perf_df["SMS"].sum(),
                "İmza": perf_df["İmza"].sum(),
                "KS-PE": perf_df["KS-PE"].sum()
            }
            fig_pie = px.pie(
                names=list(channel_totals.keys()),
                values=list(channel_totals.values()),
                hole=0.5,
                color_discrete_sequence=['#0D6EFD', '#F57C00', '#2E7D32']
            )
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.subheader("📋 Genel Performans Tablosu")
        st.dataframe(perf_df, use_container_width=True)
        
    elif raw_df is not None and missing_columns is not None:
        st.success("✅ Dosya başarıyla yüklendi!")
        st.info("ℹ️ Yüklenen dosya (Örn: F4 Ödeme Listesi) borç/cari verileri içeriyor. Sayfa altından tabloyu inceleyebilirsiniz.")
        st.dataframe(raw_df, use_container_width=True)
    else:
        st.info("💡 Sol menüden **AT ZİMMET İZLEME** veya **F4 ÖDEME LİSTESİ** dosyanızı yükleyerek paneli kullanabilirsiniz.")

# ==========================================
# TAB 2: KURYE PERFORMANS PANELİ
# ==========================================
elif st.session_state.active_tab == "Kurye Performans":
    st.title("🏃‍♂️ Kurye Performans Paneli")
    
    if perf_df is not None and not perf_df.empty:
        st.success(f"✅ AT ZİMMET İZLEME raporu başarıyla işlendi. Toplam **{len(perf_df)}** kurye bulundu.")
        
        for _, row in perf_df.iterrows():
            p_name = row["Personel"]
            zimmet = row["Zimmet"]
            teslim = row["Teslim Edilen"]
            devir = row["Teslim Edilemeyen"]
            rate = row["Başarı Oranı"]
            sms = row["SMS"]
            imza = row["İmza"]
            ks_pe = row["KS-PE"]

            avatar_url = f"https://ui-avatars.com/api/?name={p_name.replace(' ', '+')}&background=0B172E&color=F57C00&bold=true&size=80"

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
                    <div style="text-align: center;">
                        <div class="metric-title">Zimmet Sayısı</div>
                        <div class="metric-value" style="color: #FFFFFF;">{zimmet}</div>
                    </div>
                    <div style="text-align: center;">
                        <div class="metric-title">Teslim Edilen</div>
                        <div class="metric-value" style="color: #4CAF50;">{teslim}</div>
                    </div>
                    <div style="text-align: center;">
                        <div class="metric-title">Teslim Edilemeyen</div>
                        <div class="metric-value" style="color: #F44336;">{devir}</div>
                    </div>
                    <div style="text-align: center; min-width: 80px;">
                        <div class="metric-title">Başarı Oranı</div>
                        <div class="metric-value" style="color: #F57C00;">%{rate}</div>
                    </div>
                </div>
                <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.06);">
                    <div class="channel-badge">📲 SMS: <span class="badge-val">{sms}</span></div>
                    <div class="channel-badge">✍️ İMZA: <span class="badge-val">{imza}</span></div>
                    <div class="channel-badge">🚪 KS-PE: <span class="badge-val">{ks_pe}</span></div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
    else:
        st.warning("⚠️ Kurye performans kartlarını görmek için sol menüden **AT ZİMMET İZLEME** dosyasını yükleyin.")

# ==========================================
# TAB 3: OPERATÖR PERFORMANS PANELİ
# ==========================================
elif st.session_state.active_tab == "Operatör Performans":
    st.title("👩‍💼 Operatör & Acente İçi Performans")
    
    if perf_df is not None and not perf_df.empty:
        st.subheader("📌 Acente İçi Teslimat İşlemleri")
        st.dataframe(perf_df[["Personel", "Teslim Edilen", "İmza", "KS-PE"]], use_container_width=True)
    elif raw_df is not None:
        st.dataframe(raw_df, use_container_width=True)
    else:
        st.info("💡 Operatör verileri için sol taraftan dosyanızı yükleyin.")

# ==========================================
# TAB 4: GENEL RAPORLAMA VE ANALİZ
# ==========================================
elif st.session_state.active_tab == "Genel Raporlama":
    st.title("📈 Genel Raporlama ve İstatistikler")
    
    if perf_df is not None and not perf_df.empty:
        st.subheader("📊 Kuryeler Arası Zimmet vs Teslimat Karşılaştırması")
        fig_comp = go.Figure(data=[
            go.Bar(name='Teslim Edilen', x=perf_df['Personel'], y=perf_df['Teslim Edilen'], marker_color='#2E7D32'),
            go.Bar(name='Teslim Edilemeyen', x=perf_df['Personel'], y=perf_df['Teslim Edilemeyen'], marker_color='#D32F2F')
        ])
        fig_comp.update_layout(barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_comp, use_container_width=True)
    elif raw_df is not None:
        st.dataframe(raw_df, use_container_width=True)
    else:
        st.info("💡 Grafik analizi için dosya yüklemesi yapın.")
