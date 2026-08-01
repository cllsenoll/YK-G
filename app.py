# ==========================================
# TAB 2: KURYE PERFORMANS PANELİ
# ==========================================
elif st.session_state.active_tab == "Kurye Performans":
    st.title("🏃‍♂️ Kurye Performans Paneli")
    
    perf_df = st.session_state.perf_df
    if perf_df is not None and not perf_df.empty:
        st.success(f"✅ AT ZİMMET İZLEME raporu aktif. Toplam **{len(perf_df)}** kurye bulundu.")
        
        all_personnel = ["Tümü"] + sorted(perf_df["Personel"].dropna().unique().tolist())
        selected_personnel = st.selectbox("🔍 Personel Seçerek Süzgeçle:", all_personnel)
        
        if selected_personnel != "Tümü":
            filtered_perf_df = perf_df[perf_df["Personel"] == selected_personnel]
        else:
            filtered_perf_df = perf_df
            
        for idx, row in filtered_perf_df.iterrows():
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
            
