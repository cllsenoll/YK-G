import streamlit as st
import pandas as pd
import re

# ==========================================
# TÜRKÇE PARS VE TEMİZLEME FONKSİYONLARI
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

# ==========================================
# PERSONEL HESAP ALIMI EKRANI PARSER
# ==========================================
def process_personnel_account_data(df):
    header_idx = 0
    for idx, row in df.iterrows():
        row_str = " ".join([str(val).upper() for val in row.values])
        if "PERSONEL" in row_str or "NAKİT" in row_str or "FT" in row_str or "ÖDEME" in row_str:
            header_idx = idx
            break
            
    if header_idx > 0:
        df.columns = df.iloc[header_idx].astype(str).str.strip()
        df = df.iloc[header_idx + 1:].reset_index(drop=True)
    else:
        df.columns = df.columns.astype(str).str.strip()

    cols_to_drop = [c for c in df.columns if "AÇIKLAMA" in str(c).upper() or "ACIKLAMA" in str(c).upper()]
    df = df.drop(columns=cols_to_drop, errors='ignore')

    p_col, ft_col, odeme_col, banka_col = None, None, None, None

    for col in df.columns:
        c_upper = str(col).upper()
        if ("PERSONEL" in c_upper or "AD" in c_upper or "KURYE" in c_upper) and not p_col:
            p_col = col
        elif ("FT" in c_upper or "FATURA" in c_upper) and not ft_col:
            ft_col = col
        elif ("ÖDEME" in c_upper or "ODEME" in c_upper) and not odeme_col:
            odeme_col = col
        elif ("BANKA" in c_upper or "ATM" in c_upper or "POS" in c_upper) and not banka_col:
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
            
        ft_val = parse_turkish_float(row[ft_col]) if ft_col else 0.0
        odeme_val = parse_turkish_float(row[odeme_col]) if odeme_col else 0.0
        banka_val = parse_turkish_float(row[banka_col]) if banka_col else 0.0

        parsed_rows.append({
            "Raw_Name": raw_p_name,
            "Clean_Name": c_p_name,
            "Nakit Ft Tutarı Topl": ft_val,
            "Nakit Ödeme Tutarı Topl": odeme_val,
            "Banka/ATM": banka_val
        })

    temp_df = pd.DataFrame(parsed_rows)

    priority_list = [
        "HATİCE KÜBRA IŞIK",
        "ALATTİN CEBECİ",
        "BURCU DÜREN",
        "AHMET BERKAN ÖKSÜZ",
        "HASAN SAĞLAM",
        "MEHMET KAYMAZ",
        "SUAT ARI",
        "SERGEN GÖRÜROĞLU"
    ]

    final_rows = []
    processed_clean_names = set()

    for fixed_name in priority_list:
        clean_fixed = clean_string(fixed_name)
        matched_row = None
        
        if not temp_df.empty:
            exact_match = temp_df[temp_df["Clean_Name"] == clean_fixed]
            if not exact_match.empty:
                matched_row = exact_match.iloc[0]
            else:
                contains_match = temp_df[temp_df["Clean_Name"].apply(lambda x: clean_fixed in x or x in clean_fixed)]
                if not contains_match.empty:
                    matched_row = contains_match.iloc[0]

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
            c_name = row["Clean_Name"]
            if c_name not in processed_clean_names:
                final_rows.append({
                    "Personel Adı": row["Raw_Name"],
                    "Nakit Ft Tutarı Topl": float(row["Nakit Ft Tutarı Topl"]),
                    "Nakit Ödeme Tutarı Topl": float(row["Nakit Ödeme Tutarı Topl"]),
                    "Banka/ATM": float(row["Banka/ATM"]),
                })
                processed_clean_names.add(c_name)

    result_df = pd.DataFrame(final_rows)
    result_df["Hesap"] = result_df["Nakit Ft Tutarı Topl"] + result_df["Nakit Ödeme Tutarı Topl"] - result_df["Banka/ATM"]
    result_df["İşlem"] = False

    result_df.reset_index(drop=True, inplace=True)
    result_df.index = range(1, len(result_df) + 1)

    return result_df[["Personel Adı", "Nakit Ft Tutarı Topl", "Nakit Ödeme Tutarı Topl", "Banka/ATM", "Hesap", "İşlem"]]


# ==========================================
# TAB 3: GÜNLÜK HESAP EKRANI (Arayüz Kodu)
# ==========================================
# Not: `account_df` değişkeninin daha önce yüklenmiş ve işlenmiş bir pandas DataFrame olduğunu varsayar.
if 'account_df' not in st.session_state:
    st.session_state.account_df = None

account_df = st.session_state.account_df

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
