p_name = row["Personel"]
            p_zimmet = row["Zimmet"]
            p_teslim = row["Teslim Edilen"]
            p_devir = row["Teslim Edilemeyen"]
            p_oran = row["Başarı Oranı"]
            p_sms = row["SMS"]
            p_imza = row["İmza"]
            p_ks_pe = row["KS-PE"]
            
            photo_url = get_courier_photo(p_name)
            
            st.markdown(f"""
            <div class="person-card">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                    <div class="profile-section">
                        <img src="{photo_url}" class="avatar-circle">
                        <div>
                            <div class="person-name">{p_name}</div>
                            <div style="margin-top: 4px;">
                                <span class="channel-badge">SMS: <span class="badge-val">{p_sms}</span></span>
                                <span class="channel-badge">İmza: <span class="badge-val">{p_imza}</span></span>
                                <span class="channel-badge">KS-PE: <span class="badge-val">{p_ks_pe}</span></span>
                            </div>
                        </div>
                    </div>
                    <div style="display: flex; gap: 20px; align-items: center; text-align: center;">
                        <div>
                            <div class="metric-title">Zimmet</div>
                            <div class="metric-value">{p_zimmet}</div>
                        </div>
                        <div>
                            <div class="metric-title">Teslim</div>
                            <div class="metric-value" style="color: #2E7D32;">{p_teslim}</div>
                        </div>
                        <div>
                            <div class="metric-title">Devir</div>
                            <div class="metric-value" style="color: #D32F2F;">{p_devir}</div>
                        </div>
                        <div>
                            <div class="metric-title">Başarı</div>
                            <div class="metric-value" style="color: #F57C00;">%{p_oran}</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("💡 Sol menüden **AT ZİMMET İZLEME** dosyanızı yükleyerek kurye performanslarını detaylı kartlar halinde görüntüleyebilirsiniz.")

# ==========================================
# TAB 3: HESAP PANELİ
# ==========================================
elif st.session_state.active_tab == "HESAP":
    st.title("💰 Kasa ve Personel Hesap Takip Paneli")
    
    account_df = st.session_state.account_df
    if account_df is not None and not account_df.empty:
        st.subheader("💵 Günlük Kasa Miktarı Girişi")
        st.session_state.kasa_miktari = st.number_input(
            "Toplam Kasa Miktarı (TL)", 
            min_value=0.0, 
            value=float(st.session_state.kasa_miktari), 
            step=100.0,
            format="%.2f"
        )
        
        st.markdown("---")
        st.subheader("📋 Günlük Personel Hesap Takip Tablosu")
        st.markdown("<small style='color: rgba(255,255,255,0.7);'>Not: Tablodaki 'İşlem' sütununu kullanarak hesap onayları yapabilirsiniz.</small>", unsafe_allow_html=True)
        
        edited_account_df = st.data_editor(
            account_df,
            use_container_width=True,
            num_rows="dynamic",
            key="personnel_account_editor"
        )
        
        st.session_state.account_df = edited_account_df
        
        # Hesaplama mantığı: Toplam Hesap (Nakit Ft. Tutarı Top + Nakit Ödeme Tutarı Topl - Banka/ATM)
        toplam_hesap = edited_account_df["Hesap"].sum()
        kasa_farki = st.session_state.kasa_miktari - toplam_hesap
        
        st.markdown("""
        <div class="kasa-box">
            <h3 style="margin-top: 0; color: #F57C00 !important;">📊 Kasa & Hesap Özeti</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("📦 Toplam Personel Hesabı", f"{toplam_hesap:,.2f} TL")
        col_s2.metric("💵 Girilen Kasa Miktarı", f"{st.session_state.kasa_miktari:,.2f} TL")
        col_s3.metric("⚖️ Kasa / Hesap Farkı", f"{kasa_farki:,.2f} TL", delta=f"{kasa_farki:,.2f} TL")
        
    else:
        st.info("💡 Sol menüden personel hesap dosyanızı yükleyerek hesap takip panelini aktifleştirebilirsiniz.")

# ==========================================
# TAB 4: F4 ÖDEME LİSTESİ (Personel Bazlı PDF Özelliği Eklendi)
# ==========================================
elif st.session_state.active_tab == "F4 ÖDEME LİSTESİ":
    st.title("📋 F4 Ödeme Listesi ve Personel Dağılımı")
    
    f4_df = st.session_state.f4_df
    if f4_df is not None and not f4_df.empty:
        st.success(f"✅ F4 Ödeme listesi aktif. Toplam **{len(f4_df)}** kayıt bulundu.")
        
        # Personel bazında filtreleme seçeneği
        unique_personeller = sorted(f4_df["Personel"].dropna().unique().tolist())
        secilen_personel_f4 = st.selectbox("👤 Personel Bazında Süzgeçle:", ["Tümü"] + unique_personeller)
        
        if secilen_personel_f4 != "Tümü":
            gosterilecek_f4 = f4_df[f4_df["Personel"] == secilen_personel_f4]
        else:
            gosterilecek_f4 = f4_df
            
        st.dataframe(gosterilecek_f4, use_container_width=True)
        
        toplam_borc = gosterilecek_f4["Fatura Borcu"].sum()
        st.metric("💰 Seçilen Liste Toplam Borç", f"{toplam_borc:,.2f} TL")
        
        st.markdown("---")
        st.subheader("📄 Personel Bazlı PDF Raporu Oluştur")
        
        # PDF İndirme Özelliği (F4 Ödeme Listesini Personel Bazında Yazdırmak için)
        if st.button("📥 Seçilen Personelin F4 Listesini PDF Olarak İndir"):
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib import colors
                
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
                elements = []
                styles = getSampleStyleSheet()
                
                title_style = ParagraphStyle(
                    'TitleStyle',
                    parent=styles['Heading1'],
                    fontSize=16,
                    textColor=colors.HexColor('#032057'),
                    spaceAfter=12,
                    alignment=1
                )
                
                elements.append(Paragraph(f"GÖRÜKLE ACENTE - F4 ÖDEME LİSTESİ", title_style))
                elements.append(Paragraph(f"<b>Personel:</b> {secilen_personel_f4} | <b>Tarih:</b> {pd.Timestamp.now().strftime('%d.%m.%Y')}", styles['Normal']))
                elements.append(Spacer(1, 15))
                
                table_data = [["Müşteri Adı", "Fatura Borcu", "Açıklama"]]
                for _, r in gosterilecek_f4.iterrows():
                    table_data.append([str(r["Müşteri Adı"]), f"{r['Fatura Borcu']:,.2f} TL", str(r["Açıklama"])])
                    
                t = Table(table_data, colWidths=[250, 100, 150])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0A58CA')),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0,0), (-1,0), 8),
                    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8F9FA')),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DEE2E6')),
                ]))
                
                elements.append(t)
                elements.append(Spacer(1, 15))
                elements.append(Paragraph(f"<b>Toplam Borç:</b> {toplam_borc:,.2f} TL", styles['Normal']))
                
                doc.build(elements)
                pdf_data = buffer.getvalue()
                buffer.close()
                
                st.download_button(
                    label="💾 PDF Dosyasını İndir",
                    data=pdf_data,
                    file_name=f"F4_Odeme_Listesi_{secilen_personel_f4.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
                st.success("✅ PDF başarıyla oluşturuldu! Yukarıdaki butona tıklayarak indirebilirsiniz.")
            except Exception as pdf_err:
                st.error(f"❌ PDF oluşturulurken hata oluştu: {pdf_err}")
                
    else:
        st.info("💡 Sol menüden F4 Ödeme Listesi dosyanızı yükleyerek müşteri-personel eşleştirmelerini ve PDF döküm özelliklerini kullanabilirsiniz.")
