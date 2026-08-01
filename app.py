# Let's write and test the complete updated python code for app_entegre.py
code_content = '''import streamlit as st
import pandas as pd
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

st.set_page_config(page_title="Görükle Şube Operasyon & Tahsilat Paneli", layout="wide")

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

st.sidebar.title("Görükle Şube Paneli")
secim = st.sidebar.radio("Menü", ["Ana Panel", "Kurye Performans", "Hesap", "F4 ÖDEME LİSTESİ"])

if secim == "Ana Panel":
    st.header("🏠 Ana Panel")
    st.write("Günlük operasyonel takip ve genel göstergeler.")

elif secim == "Kurye Performans":
    st.header("📈 Kurye Performans")
    st.write("Kurye ve operatör teslimat metrikleri.")

elif secim == "Hesap":
    st.header("💰 Hesap")
    st.write("Finansal hesap ve günlük bakiye durumu.")

elif secim == "F4 ÖDEME LİSTESİ":
    st.header("💳 F4 Ödeme ve Personel Tahsilat Listesi")
    st.write("F4 Ödeme verilerini yükleyerek müşteri ve personel bazlı borç / tahsilat analizi yapın.")
    
    st.info(f"Sistemde kayıtlı toplam firma/müşteri eşleşme sayısı: **{len(firmalar_df)}**")
    
    uploaded_f4 = st.file_uploader("F4 ÖDEME adlı Excel veya CSV dosyanızı yükleyin", type=["csv", "xlsx", "xls"])
    
    if uploaded_f4 is not None:
        try:
            if uploaded_f4.name.endswith('.csv'):
                f4_df = pd.read_csv(uploaded_f4, encoding='cp1254', sep=';')
            else:
                f4_df = pd.read_excel(uploaded_f4)
            
            f4_df.columns = [str(c).strip() for c in f4_df.columns]
            st.success("F4 Ödeme dosyası başarıyla yüklendi!")
            
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
            
            merged_df = pd.merge(
                f4_df, 
                firmalar_df, 
                how='left', 
                left_on=secilen_musteri_kolonu, 
                right_on='Müşteri Adı'
            )
            
            eslesen_sayisi = merged_df['Personel'].notna().sum()
            st.write(f"📊 Toplam **{len(f4_df)}** kayıttan **{eslesen_sayisi}** tanesi şube personel listesiyle eşleşti.")
            
            personeller = sorted([p for p in firmalar_df['Personel'].dropna().unique()])
            secilen_personel = st.selectbox("Analiz Edilecek Personeli Seçiniz", options=personeller)
            
            personel_bazli = merged_df[merged_df['Personel'] == secilen_personel]
            
            st.markdown(f"### 👤 {secilen_personel} - Örtüşen Müşteriler ve Fatura Borç Listesi")
            
            if not personel_bazli.empty:
                st.dataframe(personel_bazli, use_container_width=True)
                
                toplam_bakiye = 0.0
                if secilen_borc_kolonu in personel_bazli.columns:
                    temiz_borc = pd.to_numeric(
                        personel_bazli[secilen_borc_kolonu].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), 
                        errors='coerce'
                    ).fillna(0)
                    toplam_bakiye = temiz_borc.sum()
                    st.metric(label=f"{secilen_personel} Toplam Fatura Borcu / Tahsilat Hedefi", value=f"{toplam_bakiye:,.2f} TL")
                
                # İndirme butonları alanı
                dl_col1, dl_col2 = st.columns(2)
                with dl_col1:
                    csv_data = personel_bazli.to_csv(index=False, encoding='cp1254').encode('cp1254')
                    st.download_button(
                        label=f"📥 {secilen_personel} Listesini İndir (CSV)",
                        data=csv_data,
                        file_name=f"{secilen_personel}_f4_tahsilat_listesi.csv",
                        mime="text/csv"
                    )
                
                with dl_col2:
                    # PDF Oluşturma Fonksiyonu
                    def generate_pdf(df_data, personel_adi, toplam_tutar):
                        buffer = BytesIO()
                        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
                        elements = []
                        
                        styles = getSampleStyleSheet()
                        
                        # Türkçe karakter desteği için standart Helvetica kullanımı veya sistem fontu
                        title_style = ParagraphStyle(
                            'TitleStyle',
                            parent=styles['Heading1'],
                            fontName='Helvetica-Bold',
                            fontSize=14,
                            textColor=colors.HexColor('#1f77b4'),
                            spaceAfter=10
                        )
                        
                        normal_style = ParagraphStyle(
                            'NormalStyle',
                            parent=styles['Normal'],
                            fontName='Helvetica',
                            fontSize=9,
                            textColor=colors.HexColor('#333333')
                        )
                        
                        elements.append(Paragraph(f"<b>Görükle Şube - {personel_adi} Tahsilat Listesi</b>", title_style))
                        elements.append(Paragraph(f"Toplam Borç / Tutar: <b>{toplam_tutar:,.2f} TL</b>", normal_style))
                        elements.append(Spacer(1, 12))
                        
                        # Tablo Verileri
                        headers = list(df_data.columns[:6]) # İlk 6 sütun sığması için
                        table_data = [[Paragraph(f"<b>{h}</b>", normal_style) for h in headers]]
                        
                        for _, row in df_data.iterrows():
                            row_data = [Paragraph(str(row[h]), normal_style) for h in headers]
                            table_data.append(row_data)
                        
                        t = Table(table_data, colWidths=[80]*len(headers))
                        t.setStyle(TableStyle([
                            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f2f6')),
                            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                            ('TOPPADDING', (0,0), (-1,-1), 6),
                            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d3d3d3'))
                        ]))
                        
                        elements.append(t)
                        doc.build(elements)
                        buffer.seek(0)
                        return buffer.getvalue()
                    
                    pdf_bytes = generate_pdf(personel_bazli, secilen_personel, toplam_bakiye)
                    st.download_button(
                        label=f"📄 {secilen_personel} Listesini İndir (PDF)",
                        data=pdf_bytes,
                        file_name=f"{secilen_personel}_tahsilat_listesi.pdf",
                        mime="application/pdf"
                    )
            else:
                st.warning(f"Seçilen personel ({secilen_personel}) için eşleşen müşteri kaydı bulunamadı.")
            
            st.markdown("---")
            st.markdown("### 🔍 F4 Ödeme Dosyasında Olup Sistem Veritabanında (Firmalar) Bulunmayan Müşteriler")
            
            # F4 dosyasındaki müşteriler ile firmalar_df'deki müşterileri karşılaştır
            f4_musteriler = set(f4_df[secilen_musteri_kolonu].dropna().astype(str).str.strip())
            sistem_musteriler = set(firmalar_df['Müşteri Adı'].dropna().astype(str).str.strip())
            
            kayitli_olmayanlar = f4_musteriler - sistem_musteriler
            
            if kayitli_olmayanlar:
                kayitli_olmayan_df = f4_df[f4_df[secilen_musteri_kolonu].astype(str).str.strip().isin(kayitli_olmayanlar)]
                st.warning(f"F4 dosyasında yer alıp sistemde kayıtlı **olmayan** toplam **{len(kayitli_olmayanlar)}** farklı müşteri/firma tespit edildi.")
                st.dataframe(kayitli_olmayan_df, use_container_width=True)
                
                unmatched_csv = kayitli_olmayan_df.to_csv(index=False, encoding='cp1254').encode('cp1254')
                st.download_button(
                    label="📥 Sisteme Kayıtlı Olmayan Müşterileri İndir (CSV)",
                    data=unmatched_csv,
                    file_name="sistemde_olmayan_musteriler.csv",
                    mime="text/csv"
                )
            else:
                st.success("Tebrikler! F4 Ödeme dosyasındaki tüm müşteriler sistem veritabanında (Firmalar) eksiksiz olarak kayıtlı.")
                
        except Exception as e:
            st.error(f"Dosya okunurken veya analiz edilirken bir hata oluştu: {e}")
    else:
        st.info("Lütfen işlem yapmak için F4 Ödeme dosyanızı yükleyin.")
'''

with open('app_entegre.py', 'w', encoding='utf-8') as f:
    f.write(code_content)

print("Successfully updated app_entegre.py!")
