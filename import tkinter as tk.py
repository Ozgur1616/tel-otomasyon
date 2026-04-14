import streamlit as st
from datetime import datetime
import pandas as pd

# ------------------ SAYFA AYARLARI ------------------
st.set_page_config(page_title="Tel Montaj Otomasyonu", layout="wide")

# Sabit Fiyatlar
MONTAJ_SABIT = 100
METRE_FIYATI = 70

# Veri Saklama
if 'siparisler' not in st.session_state:
    st.session_state.siparisler = []

# ------------------ WEB ARAYÜZÜ ------------------
st.title("🛡️ Tel Montaj Sipariş & Hesaplama Sistemi")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📋 Müşteri ve İş Bilgisi")
    musteri = st.text_input("Müşteri Adı/Soyadı", placeholder="Örn: Ahmet Yılmaz")
    metre = st.number_input("Kaç Metre Tel Döşenecek?", min_value=0.0, step=1.0)
    
    # Hesaplama Mantığı
    malzeme_tutari = metre * METRE_FIYATI
    toplam_tutar = MONTAJ_SABIT + malzeme_tutari
    
    st.divider()
    st.write(f"🛠️ Sabit Montaj: **{MONTAJ_SABIT} TL**")
    st.write(f"🏗️ Malzeme ({metre}m x {METRE_FIYATI}TL): **{malzeme_tutari} TL**")
    st.subheader(f"💰 Toplam: {toplam_tutar} TL")

with col2:
    st.subheader("📤 Sipariş Kaydı")
    notlar = st.text_area("Ek Notlar", placeholder="Örn: Bahçe kapısı yanından başlanacak...")
    
    if st.button("SİPARİŞİ KAYDET VE ONAYLA", type="primary", use_container_width=True):
        if musteri and metre > 0:
            yeni_siparis = {
                "Müşteri": musteri,
                "Metraj": f"{metre} m",
                "Toplam Tutar": f"{toplam_tutar} TL",
                "Tarih": datetime.now().strftime('%d.%m.%Y %H:%M'),
                "Notlar": notlar
            }
            st.session_state.siparisler.append(yeni_siparis)
            st.success(f"{musteri} için sipariş başarıyla kaydedildi!")
        else:
            st.error("Lütfen müşteri adını ve metre bilgisini girin.")

# ------------------ SİPARİŞ GEÇMİŞİ ------------------
st.divider()
st.subheader("📑 Alınan Siparişler Listesi")
if st.session_state.siparisler:
    df = pd.DataFrame(st.session_state.siparisler)
    st.table(df)
else:
    st.info("Henüz kaydedilmiş bir sipariş bulunmuyor.")