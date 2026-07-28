# --- EXCEL / DUMMY VERİ YÜKLEME ---
st.sidebar.title("⚙️ Veri Kaynağı")
uploaded_file = st.sidebar.file_uploader("KPOS Excel Dosyası Yükleyin", type=["xlsx", "xls"])

@st.cache_data
def get_default_data():
    return pd.DataFrame({
        "Kurye": ["Ahmet Berkant Öksüz", "Allattin Cobeci", "Hasan Sağlam", "Mehmet Kaymaz", "Suat Arı"],
        "Zimmet": [266, 250, 247, 246, 240],
        "Teslim": [228, 218, 212, 213, 207],
        "Devir": [37, 32, 35, 33, 33],
        "Sms": [150, 140, 130, 145, 135],
        "İmza": [78, 78, 82, 68, 72],
        "Nakit": [12500.0, 18000.0, 14200.0, 9800.0, 11000.0],
        "Kart": [38000.0, 42000.0, 39000.0, 35000.0, 37480.0]
    })

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.sidebar.success("Excel başarıyla yüklendi!")
    except Exception as e:
        # Hata detayını sol panelde kırmızı kutuda gösterir
        st.sidebar.error(f"Excel okunurken hata oluştu: {e}")
        df = get_default_data()
else:
    df = get_default_data()
