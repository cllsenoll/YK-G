import streamlit as st
import pandas as pd
import io
import plotly.express as px
import os
import base64
import re

# ==========================================
# 1. SAYFA YAPILANDIRMASI
# ==========================================
st.set_page_config(
    page_title="Görükle Acente - Performance Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. OTURUM DURUMU (Session State)
# ==========================================
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Ana Panel"

KULLANICI_ISIM = "Celal ŞENOL"
KULLANICI_GOREV = "Şube Şefi"

# ==========================================
# 3. CSS VE TEMA STİLLERİ
# ==========================================
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
        width: 62px;
        height: 62px;
        border-radius: 50%;
        border: 2px solid #F57C00;
        object-fit: cover;
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
    .kasa-box {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 18px;
        margin-top: 20px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 4. YARDIMCI VE DÖNÜŞTÜRÜCÜ FONKSİYONLAR
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

def get_courier_photo(courier_name):
    clean_courier = clean_string(courier_name)
    search_dirs = ["kuryeler", "."]

    for target_dir in search_dirs:
        try:
            if not os.path.exists(target_dir):
                continue
            files = os.listdir(target_dir)
            for file in files:
                file_path = os.path.join(target_dir, file)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file)[1].lower().replace('.', '')
                    if ext in ['png', 'jpg', 'jpeg', 'webp']:
                        file_name_clean = clean_string(os.path.splitext(file)[0])
                        if file_name_clean == clean_courier or (file_name_clean and clean_courier and (file_name_clean in clean_courier or clean_courier in file_name_clean)):
                            with open(file_path, "rb") as image_file:
                                encoded_string = base64.b64encode(image_file.read()).decode()
                                mime_type = "image/png" if ext == "png" else f"image/{ext}"
                                return f"data:{mime_type};base64,{encoded_string}"
        except Exception:
            continue
                        
    return f"https://ui-avatars.com/api/?name={courier_name.replace(' ', '+')}&background=0B172E&color=F57C00&bold=true&size=80"

# ==========================================
# 5. GENEL DOSYA OKUMA MOTORU
# ==========================================
def smart_read_file(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    
    # 1. Excel (openpyxl)
    try:
        xl = pd.ExcelFile(io.BytesIO(file_bytes), engine='openpyxl')
        for sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name)
            if df is not None and len(df) > 0 and len(df.columns) > 0:
                return df
    except Exception:
        pass

    # 2. Excel (xlrd)
    try:
        xl = pd.ExcelFile(io.BytesIO(file_bytes), engine='xlrd')
        for sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name)
            if df is not None and len(df) > 0 and len(df.columns) > 0:
                return df
    except Exception:
        pass

    # 3. CSV
    for enc in ['cp1254', 'iso-8859-9', 'utf-8-sig', 'utf-8', 'latin1']:
        for sep in [';', ',', '\t', None]:
            try:
                engine_type = 'python' if sep is None else None
                df = pd.read_csv(io.BytesIO(file_bytes), sep=sep, encoding=enc, engine=engine_type, on_bad_lines='skip')
                if df is not None and len(df.columns) > 0 and len(df) > 0:
                    return df
            except Exception:
                continue

    raise Exception("Dosya yapısı çözümlenemedi.")

# ==========================================
# 6. AT ZİMMET İZLEME VERİ İŞLEME MOTORU (GÜNCELLENDİ)
# ==========================================
def process_excel_data(df):
    header_idx = 0
    for idx, row in df.iterrows():
        row_str = " ".join([str(val).upper() for val in row.values])
        if "KURYE" in row_str or "ZIMMET" in row_str or "TESLIM" in row_str:
            header_idx = idx
            break
            
    if header_idx >= 0:
        df.columns = df.iloc[header_idx].astype(str).str.strip()
        df = df.iloc[header_idx + 1:].reset_index(drop=True)
    else:
        df.columns = df.columns.astype(str).str.strip()

    cols = list(df.columns)
    p_kurye_col, p_zimmet_col, p_teslim_col, p_devir_col = None, None, None, None
    sms_col, imza_col, ks_col = None, None, None

    for col in cols:
        c_clean = clean_string(str(col))
        if "KURYE" in c_clean or "PERSONEL" in c_clean:
            p_kurye_col = col
        elif "ZIMMET" in c_clean:
            p_zimmet_col = col
        elif "TESLIM" in c_clean and "DEVIR" not in c_clean:
            p_teslim_col = col
        elif "DEVIR" in c_clean:
            p_devir_col = col
        elif "SMS" in c_clean:
            sms_col = col
        elif "IMZA" in c_clean:
            imza_col = col
        elif "KS" in c_clean or "KONTROL" in c_clean:
            ks_col = col

    # Fallback pozisyon indeksleri (standart KPOS yapıları için)
    if not p_kurye_col and len(cols) > 0: p_kurye_col = cols[0]
    if not p_zimmet_col and len(cols) > 1: p_zimmet_col = cols[1]
    if not p_teslim_col and len(cols) > 2: p_teslim_col = cols[2]
    if not p_devir_col and len(cols) > 3: p_devir_col = cols[3]
    if not sms_col and len(cols) > 4: sms_col = cols[4]
    if not imza_col and len(cols) > 5: imza_col = cols[5]
    if not ks_col and len(cols) > 6: ks_col = cols[6]

    if not p_kurye_col:
        return None

    summary = []
    for _, row in df.iterrows():
        p_name = str(row[p_kurye_col]).strip() if p_kurye_col in row else ""
        if not p_name or p_name.upper() in ["NAN", "NONE", "TOTAL", "TOPLAM", "GENEL TOPLAM", ""]:
            continue
            
        zimmet_cnt = parse_turkish_float(row[p_zimmet_col]) if p_zimmet_col and p_zimmet_col in row else 0
        teslim_cnt = parse_turkish_float(row[p_teslim_col]) if p_teslim_col and p_teslim_col in row else 0
        devir_cnt = parse_turkish_float(row[p_devir_col]) if p_devir_col and p_devir_col in row else 0
        
        if zimmet_cnt == 0 and (teslim_cnt > 0 or devir_cnt > 0):
            zimmet_cnt = teslim_cnt + devir_cnt

        success_rate = round((teslim_cnt / zimmet_cnt) * 100, 1) if zimmet_cnt > 0 else 0.0

        summary.append({
            "Personel": p_name,
            "Zimmet": int(zimmet_cnt),
            "Teslim Edilen": int(teslim_cnt),
            "Teslim Edilemeyen": int(devir_cnt),
            "Başarı Oranı": success_rate,
            "SMS": int(parse_turkish_float(row[sms_col]) if sms_col and sms_col in row else 0),
            "İmza": int(parse_turkish_float(row[imza_col]) if imza_col and imza_col in row else 0),
            "KS-PE": int(parse_turkish_float(row[ks_col]) if ks_col and ks_col in row else 0)
        })

    res_df = pd.DataFrame(summary)
    if not res_df.empty:
        res_df.index = range(1, len(res_df) + 1)
    return res_df

# ==========================================
# 7. PERSONEL HESAP ALIMI EKRANI PARSER
# ==========================================
def process_personnel_account_data(df):
    header_idx = 0
    for idx, row in df.iterrows():
        row_str = " ".join([str(val).upper() for val in row.values])
        if "PERSONEL" in row_str or "NAKIT" in row_str or "FT" in row_str or "ODEME" in row_str:
            header_idx = idx
            break
            
    if header_idx > 0:
        df.columns = df.iloc[header_idx].astype(str).str.strip()
        df = df.iloc[header_idx + 1:].reset_index(drop=True)
    else:
        df.columns = df.columns.astype(str).str.strip()

    df = df.drop(columns=[c for c in df.columns if "ACIKLAMA" in clean_string(str(c))], errors='ignore')

    p_col, ft_col, odeme_col, banka_col = None, None, None, None
    for col in df.columns:
        c_clean = clean_string(str(col))
        if ("PERSONEL" in c_clean or "AD" in c_clean or "KURYE" in c_clean) and not p_col:
            p_col = col
        elif ("FT" in c_clean or "FATURA" in c_clean) and not ft_col:
            ft_col = col
        elif ("ODEME" in c_clean) and not odeme_col:
            odeme_col = col
        elif ("BANKA" in c_clean or "ATM" in c_clean or "POS" in c_clean) and not banka_col:
            banka_col = col

    cols_list = list(df.columns)
    if not p_col and len(cols_list) > 0: p_col = cols_list[0]
    if not ft_col and len(cols_list) > 1: ft_col = cols_list[1]
    if not odeme_col and len(cols_list) > 2: odeme_col = cols_list[2]
    if not banka_col and len(cols_list) > 3: banka_col = cols_list[3]

    parsed_rows = []
    for _, row in df.iterrows():
        raw_p_name = str(row[p_col]).strip() if p_col else ""
        c_p_name = clean_string(raw_p_name)
        if not c_p_name or c_p_name in ["NAN", "NONE", "TOTAL", "TOPLAM", "GENELTOPLAM"]:
            continue
            
        parsed_rows.append({
            "Raw_Name": raw_p_name,
            "Clean_Name": c_p_name,
            "Nakit Ft Tutarı Topl": parse_turkish_float(row[ft_col]) if ft_col else 0.0,
            "Nakit Ödeme Tutarı Topl": parse_turkish_float(row[odeme_col]) if odeme_col else 0.0,
            "Banka/ATM": parse_turkish_float(row[banka_col]) if banka_col else 0.0
        })

    temp_df = pd.DataFrame(parsed_rows)
    priority_list = [
        "HATİCE KÜBRA IŞIK", "ALATTİN CEBECİ", "BURCU DÜREN", 
        "AHMET BERKAN ÖKSÜZ", "HASAN SAĞLAM", "MEHMET KAYMAZ", 
        "SUAT ARI", "SERGEN GÖRÜROĞLU"
    ]

    final_rows = []
    processed_clean_names = set()

    for fixed_name in priority_list:
        clean_fixed = clean_string(fixed_name)
        matched_row = None
        if not temp_df.empty:
            exact = temp_df[temp_df["Clean_Name"] == clean_fixed]
            if not exact.empty:
                matched_row = exact.iloc[0]
            else:
                contains = temp_df[temp_df["Clean_Name"].apply(lambda x: clean_fixed in x or x in clean_fixed)]
                if not contains.empty:
                    matched_row = contains.iloc[0]

        if matched_row is not None:
            final_rows.append({
                "Personel Adı": fixed_name,
                "Nakit Ft Tutarı Topl": float(matched_row["Nakit Ft Tutarı Topl"]),
                "Nakit Ödeme Tutarı Topl": float(matched_row["Nakit Ödeme Tutarı Topl"]),
                "Banka/ATM": float(matched_row["Banka/ATM"]),
            })
            processed_clean_names.add(matched_row["Clean_Name"])
        else:
            final_rows.append({
                "Personel Adı": fixed_name,
                "Nakit Ft Tutarı Topl": 0.0,
                "Nakit Ödeme Tutarı Topl": 0.0,
                "Banka/ATM": 0.0,
            })

    if not temp_df.empty:
        for _, row in temp_df.iterrows():
            if row["Clean_Name"] not in processed_clean_names:
                final_rows.append({
                    "Personel Adı": row["Raw_Name"],
                    "Nakit Ft Tutarı Topl": float(row["Nakit Ft Tutarı Topl"]),
                    "Nakit Ödeme Tutarı Topl": float(row["Nakit Ödeme Tutarı Topl"]),
                    "Banka/ATM": float(row["Banka/ATM"]),
                })
                processed_clean_names.add(row["Clean_Name"])

    result_df = pd.DataFrame(final_rows)
    result_df["Hesap"] = result_df["Nakit Ft Tutarı Topl"] + result_df["Nakit Ödeme Tutarı Topl"] - result_df["Banka/ATM"]
    result_df["İşlem"] = False
    result_df.index = range(1, len(result_df) + 1)
    return result_df[["Personel Adı", "Nakit Ft Tutarı Topl", "Nakit Ödeme Tutarı Topl", "Banka/ATM", "Hesap", "İşlem"]]

# ==========================================
# 8. SIDEBAR VE GEZİNTİ MENÜSÜ
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

    uploaded_files = st.file_uploader("📂 Rapor / Listeleri Yükle (Çoklu Seçebilirsiniz)", type=None, accept_multiple_files=True)
    
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    if st.button("📊 Ana Panel"):
        st.session_state.active_tab = "Ana Panel"
    if st.button("🏃‍♂️ Kurye Performans"):
        st.session_state.active_tab = "Kurye Performans"
    if st.button("📋 Günlük Hesap"):
        st.session_state.active_tab = "Günlük Hesap"

# ==========================================
# 9. DOSYALARIN OTURUMDA SAKLANMASI (KALICI HAFIZA)
# ==========================================
if 'perf_df' not in st.session_state:
    st.session_state.perf_df = None
if 'account_df' not in st.session_state:
    st.session_state.account_df = None

if uploaded_files:
    for file in uploaded_files:
        try:
            temp_raw = smart_read_file(file)
            full_text = " ".join([clean_string(str(c)) for c in temp_raw.columns]) + " " + " ".join([clean_string(str(val)) for val in temp_raw.iloc[0:min(5, len(temp_raw))].values.flatten()])
            
            # AT ZİMMET İZLEME KONTROLÜ
            if "ZIMMET" in full_text or "TESLIM" in full_text or "DEVIR" in full_text:
                res = process_excel_data(temp_raw)
                if res is not None and not res.empty:
                    st.session_state.perf_df = res
            
            # PERSONEL HESAP KONTROLÜ
            if "NAKIT" in full_text or "BANKA" in full_text or "ODEME" in full_text or "FT" in full_text:
                res_acc = process_personnel_account_data(temp_raw)
                if res_acc is not None and not res_acc.empty:
                    st.session_state.account_df = res_acc
                    if 'hesap_df' not in st.session_state:
                        st.session_state.hesap_df = res_acc.copy()
        except Exception as e:
            st.error(f"❌ {file.name} işlenirken hata oluştu: {e}")

perf_df = st.session_state.perf_df
account_df = st.session_state.account_df

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
            fig_bar = px.bar(perf_df, x="Personel", y="Başarı Oranı", color="Başarı Oranı", color_continuous_scale="RdYlGn", text="Başarı Oranı")
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_right:
            st.subheader("📲 Teslimat Kanalları Dağılımı")
            channel_totals = {"SMS": perf_df["SMS"].sum(), "İmza": perf_df["İmza"].sum(), "KS-PE": perf_df["KS-PE"].sum()}
            fig_pie = px.pie(names=list(channel_totals.keys()), values=list(channel_totals.values()), hole=0.5, color_discrete_sequence=['#0D6EFD', '#F57C00', '#2E7D32'])
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.subheader("📋 Genel Performans Tablosu")
        st.dataframe(perf_df, use_container_width=True)
    else:
        st.info("💡 Sol taraftan **AT ZİMMET İZLEME** dosyanızı yükleyerek verileri görüntüleyebilirsiniz.")

# ==========================================
# TAB 2: KURYE PERFORMANS PANELİ
# ==========================================
elif st.session_state.active_tab == "Kurye Performans":
    st.title("🏃‍♂️ Kurye Performans Paneli")
    
    if perf_df is not None and not perf_df.empty:
        st.success(f"✅ Aktif kurye verisi yüklü. Toplam **{len(perf_df)}** kurye listeleniyor.")
        for _, row in perf_df.iterrows():
            avatar_url = get_courier_photo(row["Personel"])
            card_html = f"""
            <div class="person-card notranslate">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
                    <div class="profile-section" style="min-width: 220px;">
                        <img src="{avatar_url}" class="avatar-circle">
                        <div>
                            <div class="person-name">{row["Personel"]}</div>
                            <small style="color: #F57C00;">Saha Kuryesi</small>
                        </div>
                    </div>
                    <div style="text-align: center;"><div class="metric-title">Zimmet</div><div class="metric-value">{row["Zimmet"]}</div></div>
                    <div style="text-align: center;"><div class="metric-title">Teslim</div><div class="metric-value" style="color: #4CAF50;">{row["Teslim Edilen"]}</div></div>
                    <div style="text-align: center;"><div class="metric-title">Devir</div><div class="metric-value" style="color: #F44336;">{row["Teslim Edilemeyen"]}</div></div>
                    <div style="text-align: center;"><div class="metric-title">Başarı</div><div class="metric-value" style="color: #F57C00;">%{row["Başarı Oranı"]}</div></div>
                </div>
                <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.06);">
                    <div class="channel-badge">📲 SMS: <span class="badge-val">{row["SMS"]}</span></div>
                    <div class="channel-badge">✍️ İMZA: <span class="badge-val">{row["İmza"]}</span></div>
                    <div class="channel-badge">🚪 KS-PE: <span class="badge-val">{row["KS-PE"]}</span></div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Kurye kartlarını görmek için sol menüden **AT ZİMMET İZLEME** dosyasını yükleyin.")

# ==========================================
# TAB 3: GÜNLÜK HESAP
# ==========================================
elif st.session_state.active_tab == "Günlük Hesap":
    st.title("📋 Günlük Personel Hesap Takip Tablosu")
    st.caption("✍️ Değerleri değiştirdiğinizde **Hesap** alanı canlı olarak güncellenir.")
    
    if account_df is not None:
        if "hesap_df" not in st.session_state or st.sidebar.button("🔄 Tabloyu Sıfırla"):
            st.session_state.hesap_df = account_df.copy()
            
        current_df = st.session_state.hesap_df.copy()

        def highlight_rows(row):
            if row.get('İşlem', False):
                return ['background-color: rgba(46, 125, 50, 0.4); color: #ffffff; font-weight: bold;'] * len(row)
            return [''] * len(row)

        edited_output = st.data_editor(
            current_df.style.apply(highlight_rows, axis=1),
            column_config={
                "Personel Adı": st.column_config.TextColumn("Personel Adı", required=True),
                "Nakit Ft Tutarı Topl": st.column_config.NumberColumn("Nakit Ft Tutarı Topl", format="%.2f ₺"),
                "Nakit Ödeme Tutarı Topl": st.column_config.NumberColumn("Nakit Ödeme Tutarı Topl", format="%.2f ₺"),
                "Banka/ATM": st.column_config.NumberColumn("Banka/ATM", format="%.2f ₺"),
                "Hesap": st.column_config.NumberColumn("Hesap", format="%.2f ₺", disabled=True),
                "İşlem": st.column_config.CheckboxColumn("İşlem (Tamamlandı)", default=False)
            },
            disabled=["Hesap"],
            hide_index=False,
            use_container_width=True,
            num_rows="fixed"
        )

        edited_df = pd.DataFrame(edited_output)
        ft_vals = pd.to_numeric(edited_df["Nakit Ft Tutarı Topl"], errors='coerce').fillna(0.0)
        odeme_vals = pd.to_numeric(edited_df["Nakit Ödeme Tutarı Topl"], errors='coerce').fillna(0.0)
        banka_vals = pd.to_numeric(edited_df["Banka/ATM"], errors='coerce').fillna(0.0)
        edited_df["Hesap"] = ft_vals + odeme_vals - banka_vals
        st.session_state.hesap_df = edited_df

        st.markdown("<div class='kasa-box'>", unsafe_allow_html=True)
        st.subheader("💵 Genel Kasa ve Hesap Dengesi")
        toplam_hesap = float(edited_df["Hesap"].sum())

        col1, col2, col3 = st.columns(3)
        col1.metric("📊 Toplam Hesap", f"{toplam_hesap:,.2f} ₺")

        if "kasa_miktari" not in st.session_state:
            st.session_state.kasa_miktari = 0.0
        kasa_val = col2.number_input("🏦 KASA (Manuel Giriniz)", value=float(st.session_state.kasa_miktari), step=100.0, format="%.2f")
        st.session_state.kasa_miktari = kasa_val

        kasa_fark = toplam_hesap - kasa_val
        if kasa_val > toplam_hesap:
            col3.metric("⚖️ Kasa Farkı Durumu", f"{kasa_fark:,.2f} ₺", delta="Durum: AÇIK", delta_color="inverse")
        else:
            col3.metric("⚖️ Kasa Farkı Durumu", f"{kasa_fark:,.2f} ₺", delta="Durum: TAM", delta_color="normal")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("💡 Lütfen sol taraftan **PERSONEL HESAP ALIMI EKRANI** dosyanızı yükleyin.")
