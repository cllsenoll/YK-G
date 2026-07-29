import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# 1. SAYFA AYARLARI
st.set_page_config(
    page_title="Yurtiçi Kargo Görükle Acente",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. OTURUM DURUMU
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Kurye Performans"

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
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# AKILLI DOSYA OKUMA MOTORU (HTML/XML/CSV/EXCEL)
# ==========================================
def load_uploaded_file(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    errors = []

    # 1. HTML Tablo Denemesi (Sistem raporları genelde HTML tablosudur)
    try:
        dfs = pd.read_html(io.BytesIO(file_bytes), encoding='utf-8')
        if dfs and len(dfs) > 0:
            return dfs[0]
    except Exception as e:
        errors.append(f"HTML (utf-8): {e}")

    try:
        dfs = pd.read_html(io.BytesIO(file_bytes), encoding='latin1')
        if dfs and len(dfs) > 0:
            return dfs[0]
    except Exception as e:
        errors.append(f"HTML (latin1): {e}")

    # 2. XLSX (OpenPyXL)
    try:
        return pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
    except Exception as e:
        errors.append(f"OpenPyXL: {e}")

    # 3. XLS (XLRD)
    try:
        return pd.read_excel(io.BytesIO(file_bytes), engine='xlrd')
    except Exception as e:
        errors.append(f"XLRD: {e}")

    # 4. CSV - Noktalı Virgül (Sistem çıktıları genelde böyledir)
    try:
        return pd.read_csv(io.BytesIO(file_bytes), sep=';', encoding='utf-8')
    except Exception as e:
        errors.append(f"CSV (; utf-8): {e}")

    try:
        return pd.read_csv(io.BytesIO(file_bytes), sep=';', encoding='latin1')
    except Exception as e:
        errors.append(f"CSV (; latin1): {e}")

    # 5. CSV - Virgül
    try:
        return pd.read_csv(io.BytesIO(file_bytes), sep=',', encoding='utf-8')
    except Exception as e:
        errors.append(f"CSV (, utf-8): {e}")

    # 6. CSV - Tab ile ayrılmış (TSV)
    try:
        return pd.read_csv(io.BytesIO(file_bytes), sep='\t', encoding='utf-8')
    except Exception as e:
        errors.append(f"TSV (utf-8): {e}")

    # Hiçbiri çalışmazsa hataları göster
    error_msg = " | ".join(errors)
    raise ValueError(f"Dosya hiçbir yöntemle okunamadı. Detaylar: {error_msg}")

# ==========================================
# VERİ İŞLEME MOTORU (EXCEL PARSER)
# ==========================================
def process_excel_data(df):
    # Kolon İsimlerini Temizle
    df.columns = df.columns.astype(str).str.strip()
    
    # Zorunlu Kolon Kontrolü
    req_cols = ["AT Zimmet Personel Adı", "Teslim Eden Personel", "Kargo Teslimat Kanalı"]
    missing_cols = [col for col in req_cols if col not in df.columns]
    
    if missing_cols:
        st.error(f"❌ Excel/Rapor dosyasında şu sütunlar bulunamadı: {', '.join(missing_cols)}")
        st.info(f"📋 Tespit Edilen Sütunlar: {list(df.columns)}")
        return None

    has_aciklama = "Açıklama" in df.columns

    # Teslim Mantığı: AT Zimmet Personel Adı == Teslim Eden Personel
    def check_delivery(row):
        zimmet_p = str(row["AT Zimmet Personel Adı"]).strip().upper()
        teslim_p = str(row["Teslim Eden Personel"]).strip().upper()
        return (zimmet_p == teslim_p) and (zimmet_p != "" and zimmet_p != "NAN")

    # Kanal Mantığı: Kontrol Sende veya POS Entegrasyon -> KS-PE
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

    # Personel Bazlı Özet (Tamamen Yüklenen Dosyadan Alınır)
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

    return pd.DataFrame(summary)

# ==========================================
# SIDEBAR (DOSYA YÜKLEME)
# ==========================================
with st.sidebar:
    st.markdown("### Yurtiçi Kargo<br><small style='color:#F57C00;'>Görükle Acente</small>", unsafe_allow_html=True)
    st.write("")
    
    uploaded_file = st.file_uploader("AT ZİMMET İZLEME Dosyası Yükle", type=None)
    
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    if st.button("🏃‍♂️ Kurye Performans"):
        st.session_state.active_tab = "Kurye Performans"

# ==========================================
# KURYELER PERFORMANS PANELİ
# ==========================================
st.subheader("🏃‍♂️ Kurye Performans Paneli")

if uploaded_file is not None:
    try:
        raw_df = load_uploaded_file(uploaded_file)
        perf_df = process_excel_data(raw_df)
        
        if perf_df is not None and not perf_df.empty:
            st.success(f"✅ Dosya başarıyla okundu! Toplam **{len(perf_df)}** kurye bulundu.")
            
            for _, row in perf_df.iterrows():
                p_name = row["Personel"]
                zimmet = row["Zimmet"]
                teslim = row["Teslim Edilen"]
                devir = row["Teslim Edilemeyen"]
                rate = row["Başarı Oranı"]
                sms = row["SMS"]
                imza = row["İmza"]
                ks_pe = row["KS-PE"]

                with st.container():
                    st.markdown(f"### 👤 {p_name}")
                    
                    col_img, col_z, col_t, col_d, col_chart = st.columns([1, 1, 1, 1, 1.2])
                    
                    with col_img:
                        avatar_url = f"https://ui-avatars.com/api/?name={p_name.replace(' ', '+')}&background=0B172E&color=F57C00&bold=true&size=80"
                        st.image(avatar_url, width=70)
                        
                    with col_z:
                        st.metric("Zimmet Sayısı", zimmet)
                        
                    with col_t:
                        st.metric("Teslim Edilen", teslim)
                        
                    with col_d:
                        st.metric("Teslim Edilemeyen", devir)
                        
                    with col_chart:
                        fig = go.Figure(data=[go.Pie(
                            labels=['Teslim', 'Devir'],
                            values=[teslim, devir],
                            hole=0.65,
                            marker_colors=['#2E7D32', '#D32F2F'],
                            textinfo='none',
                            hoverinfo='label+value'
                        )])
                        fig.update_layout(
                            showlegend=False,
                            margin=dict(l=0, r=0, t=0, b=0),
                            height=75,
                            width=75,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            annotations=[dict(
                                text=f"<b>%{rate:.0f}</b>",
                                x=0.5, y=0.5,
                                font_size=12,
                                font_color="white",
                                showarrow=False
                            )]
                        )
                        st.plotly_chart(fig, use_container_width=False, config={'displayModeBar': False})

                    st.caption(f"📲 **SMS:** {sms} adet &nbsp;&nbsp;|&nbsp;&nbsp; ✍️ **İmza:** {imza} adet &nbsp;&nbsp;|&nbsp;&nbsp; 🚪 **KS-PE:** {ks_pe} adet")
                    st.markdown("---")

    except Exception as e:
        st.error(f"❌ Dosya İşleme Hatası:\n{e}")
else:
    st.info("💡 Lütfen verilerin hesaplanması için sol menüden **AT ZİMMET İZLEME** dosyanızı yükleyin.")
