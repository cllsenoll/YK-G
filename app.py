import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Görükle Şube Operasyon & Tahsilat Paneli", layout="wide")

# Otomatik Firma / Personel Eşleştirme Verisini Yükleme Fonksiyonu
@st.cache_data
def load_firmalar():
    if os.path.exists('FİRMALAR.CSV'):
        try:
            df = pd.read_csv('FİRMALAR.CSV', encoding='cp1254', sep=';')
            df.columns = [str(c).strip() for c in df.columns]
            return df[['Müşteri Adı', 'Personel']].dropna(subset=['Müşteri Adı'])
        except Exception:
            return pd.DataFrame(columns=['Müşteri Adı', 'Personel'])
    return pd.DataFrame(columns=['Müşteri Adı', 'Personel'])

firmalar_df = load_firmalar()

# Sidebar Navigasyon Menüsü
st.sidebar.title("Görükle Şube Paneli")
secim = st.sidebar.radio("Menü", ["Ana Panel", "Kurye Performans", "Hesap", "F4 ÖDEME LİSTESİ"])

if secim == "Ana Panel":
    st.header("🏠 Ana Panel")
    st.write("Günlük operasyonel takip ve genel göstergeler.")
    # Mevcut Ana Panel kodlarınız burada yer alır

elif secim == "Kurye Performans":
    st.header("📈 Kurye Performans")
    st.write("Kurye ve operatör teslimat metrikleri.")
    # Mevcut Kurye Performans kodlarınız burada yer alır

elif secim == "Hesap":
    st.header("💰 Hesap")
    st.write("Finansal hesap ve günlük bakiye durumu.")
    # Mevcut Hesap kodlarınız burada yer alır

elif secim == "F4 ÖDEME LİSTESİ":
    st.header("💳 F4 Ödeme ve Personel Tahsilat Listesi")
    st.write("F4 Ödeme verilerini yükleyerek müşteri ve personel bazlı borç / tahsilat analizi yapın.")
    
    # Bilgi Kutusu
    st.info(f"Sistemde kayıtlı toplam firma/müşteri eşleşme sayısı: **{len(firmalar_df)}**")
    
    # F4 Ödeme Dosyası Yükleme Alanı
    uploaded_f4 = st.file_uploader("F4 ÖDEME adlı Excel veya CSV dosyanızı yükleyin", type=["csv", "xlsx", "xls"])
    
    if uploaded_f4 is not None:
        try:
            # Dosya türüne göre okuma
            if uploaded_f4.name.endswith('.csv'):
                f4_df = pd.read_csv(uploaded_f4, encoding='cp1254', sep=';')
            else:
                f4_df = pd.read_excel(uploaded_f4)
            
            # Sütun isimlerindeki boşlukları temizle
            f4_df.columns = [str(c).strip() for c in f4_df.columns]
            
            st.success("F4 Ödeme dosyası başarıyla yüklendi!")
            
            # Otomatik sütun algılama
            musteri_kolonu_f4 = None
            borc_kolonu_f4 = None
            
            for col in f4_df.columns:
                col_lower = col.lower()
                if 'müşteri' in col_lower or 'firma' in col_lower or 'unvan' in col_lower:
                    musteri_kolonu_f4 = col
                if 'borç' in col_lower or 'bakiye' in col_lower or 'tutar' in col_lower or 'tahsilat' in col_lower:
                    borc_kolonu_f4 = col
            
            col1, col2 = st.columns(2)
            with col1:
                secilen_musteri_kolonu = st.selectbox("F4 Dosyasındaki Müşteri/Firma Sütunu", options=f4_df.columns, index=list(f4_df.columns).index(musteri_kolonu_f4) if musteri_kolonu_f4 else 0)
            with col2:
                secilen_borc_kolonu = st.selectbox("F4 Dosyasındaki Borç/Tutar Sütunu", options=f4_df.columns, index=list(f4_df.columns).index(borc_kolonu_f4) if borc_kolonu_f4 else 0)
            
            # FİRMALAR.CSV ile F4 Ödeme verisinin birleştirilmesi (Merge)
            merged_df = pd.merge(
                f4_df, 
                firmalar_df, 
                how='left', 
                left_on=secilen_musteri_kolonu, 
                right_on='Müşteri Adı'
            )
            
            eslesen_sayisi = merged_df['Personel'].notna().sum()
            st.write(f"📊 Toplam **{len(f4_df)}** kayıttan **{eslesen_sayisi}** tanesi şube personel listesiyle eşleşti.")
            
            # Personel Seçimi
            personeller = sorted([p for p in firmalar_df['Personel'].dropna().unique()])
            secilen_personel = st.selectbox("Analiz Edilecek Personeli Seçiniz", options=personeller)
            
            # Seçilen personele göre filtreleme
            personel_bazli = merged_df[merged_df['Personel'] == secilen_personel]
            
            st.markdown(f"### 👤 {secilen_personel} - Örtüşen Müşteriler ve Fatura Borç Listesi")
            
            if not personel_bazli.empty:
                st.dataframe(personel_bazli, use_container_width=True)
                
                # Toplam Borç / Tahsilat Metriği
                if secilen_borc_kolonu in personel_bazli.columns:
                    temiz_borc = pd.to_numeric(
                        personel_bazli[secilen_borc_kolonu].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), 
                        errors='coerce'
                    ).fillna(0)
                    
                    toplam_bakiye = temiz_borc.sum()
                    st.metric(label=f"{secilen_personel} Toplam Fatura Borcu / Tahsilat Hedefi", value=f"{toplam_bakiye:,.2f} TL")
                
                # Listeyi İndirme Butonu
                csv_data = personel_bazli.to_csv(index=False, encoding='cp1254').encode('cp1254')
                st.download_button(
                    label=f"📥 {secilen_personel} Listesini İndir (CSV)",
                    data=csv_data,
                    file_name=f"{secilen_personel}_f4_tahsilat_listesi.csv",
                    mime="text/csv"
                )
            else:
                st.warning(f"Seçilen personel ({secilen_personel}) için eşleşen müşteri kaydı bulunamadı.")
                
        except Exception as e:
            st.error(f"Dosya okunurken veya analiz edilirken bir hata oluştu: {e}")
    else:
        st.info("Lütfen işlem yapmak için F4 Ödeme dosyanızı yükleyin.")
