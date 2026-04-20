import streamlit as st
from datetime import datetime
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ------------------ MAİL AYARLARI (BURAYI DOLDUR) ------------------
# Gmail hesabından aldığın 16 haneli uygulama şifresini 'SIFRE' kısmına yaz.
# Gonderen ve Alici mail adreslerini kendi mailinle değiştir.
GONDEREN_MAIL = "oefe02090@gmail.com"
ALICI_MAIL = "oefe02081@gmail.com"
SIFRE = "fmlftvqhyqyrkkhw" # Buraya o 16 haneli uygulama şifresini yapıştır!

def mail_gonder(siparis_detay):
    try:
        mesaj = MIMEMultipart()
        mesaj["From"] = GONDEREN_MAIL
        mesaj["To"] = ALICI_MAIL
        mesaj["Subject"] = f"YENİ SİPARİŞ: {siparis_detay['Müşteri']}"

        icerik = f"""
        Yeni bir tel montaj siparişi alındı!
        ----------------------------------
        Müşteri: {siparis_detay['Müşteri']}
        Telefon: {siparis_detay['Telefon']}
        Metraj: {siparis_detay['Metraj']}
        Toplam Tutar: {siparis_detay['Toplam Tutar']}
        Tarih: {siparis_detay['Tarih']}
        Notlar: {siparis_detay['Notlar']}
        ----------------------------------
        """
        mesaj.attach(MIMEText(icerik, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GONDEREN_MAIL, SIFRE)
        server.sendmail(GONDEREN_MAIL, ALICI_MAIL, mesaj.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

# ------------------ SAYFA AYARLARI ------------------
st.set_page_config(page_title="Tel Montaj Otomasyonu", layout="wide")

# Sabit Fiyatlar
MONTAJ_SABIT = 100
METRE_FIYATI = 70

# Veri Saklama (Session State)
if 'siparisler' not in st.session_state:
    st.session_state.siparisler = []

# ------------------ WEB ARAYÜZÜ ------------------
st.title("🛡️ Tel Montaj Sipariş & Hesaplama Sistemi")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📋 Müşteri ve İş Bilgisi")
    musteri = st.text_input("Müşteri Adı/Soyadı", placeholder="Örn: Ahmet Yılmaz")
    
    # MÜŞTERİ TELEFON GİRİŞİ
    telefon = st.text_input("Telefon Numaranız", placeholder="05xx xxx xx xx")
    
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
        # Müşteri, Telefon ve Metre bilgilerinin boş olmadığını kontrol ediyoruz
        if musteri and telefon and metre > 0:
            yeni_siparis = {
                "Müşteri": musteri,
                "Telefon": telefon,
                "Metraj": f"{metre} m",
                "Toplam Tutar": f"{toplam_tutar} TL",
                "Tarih": datetime.now().strftime('%d.%m.%Y %H:%M'),
                "Notlar": notlar
            }
            
            # 1. Maili Gönder
            mail_durumu = mail_gonder(yeni_siparis)
            
            # 2. Listeye Ekle
            st.session_state.siparisler.append(yeni_siparis)
            
            if mail_durumu:
                st.success(f"Başarılı! {musteri} adına sipariş kaydedildi ve mail gönderildi.")
            else:
                st.warning("Sipariş kaydedildi fakat mail iletilemedi (Şifreyi kontrol edin).")
        else:
            st.error("Lütfen tüm alanları (Ad, Telefon, Metre) eksiksiz doldurun.")

# ------------------ SİPARİŞ GEÇMİŞİ ------------------
st.divider()
st.subheader("📑 Alınan Siparişler Listesi")
if st.session_state.siparisler:
    df = pd.DataFrame(st.session_state.siparisler)
    st.table(df)
else:
    st.info("Henüz kaydedilmiş bir sipariş bulunmuyor.")
