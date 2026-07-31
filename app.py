# F4 Ödeme Listesi ayrıştırma fonksiyonunu güncelleyelim.
# Görüntüye göre ham veride müşteri adı ile açıklama yer değiştirmiş durumda:
# Müşteri Adı sütununda kodlar/numaralar yer alırken, asıl şirket unvanları Açıklama sütununda yazıyor.
# Bu düzeltmeyle unvanlar 'Müşteri Adı'na taşınacak ve 'Açıklama' boş bırakılacak.

updated_code_snippet = """
def process_f4_payment_data(df):
    df.columns = df.columns.astype(str).str.strip()
    
    musteri_col, borc_col, aciklama_col = None, None, None
    for col in df.columns:
        c_upper = str(col).upper()
        if ("MÜŞTERİ" in c_upper or "MUSTERI" in c_upper or "FIRMA" in c_upper or "UNVAN" in c_upper) and not musteri_col:
            musteri_col = col
        elif ("BORÇ" in c_upper or "BORC" in c_upper or "BAKİYE" in c_upper or "BAKIYE" in c_upper or "TUTAR" in c_upper) and not borc_col:
            borc_col = col
        elif "AÇIKLAMA" in c_upper or "ACIKLAMA" in c_upper:
            aciklama_col = col

    cols_list = list(df.columns)
    if not musteri_col and len(cols_list) > 0: musteri_col = cols_list[0]
    if not borc_col and len(cols_list) > 1: borc_col = cols_list[1]
    if not aciklama_col and len(cols_list) > 2: aciklama_col = cols_list[2]

    processed_rows = []
    for _, row in df.iterrows():
        # Gerçek müşteri unvanı açıklama sütununda yer aldığı için oradan alıyoruz
        m_adi = str(row[aciklama_col]).strip() if aciklama_col and not pd.isna(row[aciklama_col]) else ""
        if not m_adi or m_adi.upper() in ["NAN", "NONE", "TOPLAM", "TOTAL"]:
            # Eğer açıklama boşsa müşteri kolonuna bakabiliriz
            m_adi = str(row[musteri_col]).strip() if musteri_col else ""
            
        if not m_adi or m_adi.upper() in ["NAN", "NONE", "TOPLAM", "TOTAL"]:
            continue
            
        borc_val = parse_turkish_float(row[borc_col]) if borc_col else 0.0
        
        if borc_val == 0.0:
            continue

        processed_rows.append({
            "Müşteri Adı": m_adi,
            "Fatura Borcu": borc_val,
            "Açıklama": ""
        })

    res_df = pd.DataFrame(processed_rows)
    if not res_df.empty:
        res_df.reset_index(drop=True, inplace=True)
        res_df.index = range(1, len(res_df) + 1)
    return res_df
"""
print("F4 Ödeme Listesi ayrıştırma mantığı düzeltildi.")
