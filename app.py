import pandas as pd

# Excel dosyasını oku (dosya adınızı buraya yazın)
dosya_adi = "verileriniz.xlsx"  # Örnek dosya adı
df = pd.read_excel(dosya_adi)

# Sütun adlarının sizdeki karşılığını buraya yazın
zimmet_sutun = "AT Zimmet Personel"
teslim_eden_sutun = "Teslim Eden Personel"

# Örnek personel adı
personel_adi = "MEHMET KAYMAZ"

# 1. Zimmet Sayısı: AT Zimmet Personel sütununda adı geçen satırlar
zimmet_sayisi = (df[zimmet_sutun] == personel_adi).sum()

# 2. Teslim Edilen Sayısı: Hem AT Zimmet Personel hem Teslim Eden Personel sütununda adı geçenler
teslim_edilen_sayisi = (
    (df[zimmet_sutun] == personel_adi) & (df[teslim_eden_sutun] == personel_adi)
).sum()

# 3. Teslim Edilemeyen (Devir) Sayısı: AT Zimmet'te adı var, fakat Teslim Eden boş veya başka biri
teslim_edilemeyen_sayisi = (
    (df[zimmet_sutun] == personel_adi)
    & (
        (df[teslim_eden_sutun].isna())
        | (df[teslim_eden_sutun] != personel_adi)
    )
).sum()

print(f"Personel: {personel_adi}")
print(f"Zimmet Sayısı          : {zimmet_sayisi}")
print(f"Teslim Edilen Sayısı   : {teslim_edilen_sayisi}")
print(f"Teslim Edilemeyen (Devir): {teslim_edilemeyen_sayisi}")
