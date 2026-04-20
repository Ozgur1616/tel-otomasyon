import streamlit as st
from datetime import datetime
import pandas as pd
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ------------------ MAİL AYARLARI ------------------
GONDEREN_MAIL = "oefe02081@gmail.com"
ALICI_MAIL = "oefe02090@gmail.com"
SIFRE = "fmlftvqhyqyrkkhw" 

def mail_gonder(siparis_detay):
    try:
        mesaj = MIMEMultipart()
        mesaj["From"] = GONDEREN_MAIL
        mesaj["To"] = ALICI_MAIL
        mesaj["Subject"] = f"YENİ SİPARİŞ #{siparis_detay['Sipariş No']} - {siparis_detay['Müşteri']}"
        
        icerik = f"""
        YENİ SİPARİŞ BİLGİLERİ
        ----------------------------------
        Sipariş No: #{siparis_detay['Sipariş No']}
        Müşteri: {siparis_detay['Müşteri']}
        Telefon: {siparis_detay['Telefon']}
        
        ADRES: 
        {siparis_detay['Adres']}
        
        DETAYLAR:
        Montaj Durumu: {siparis_detay['Montaj']}
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
    except:
        return False

# ------------------ SAYFA AYARLARI ------------------
st.set_page_config(page_title="Tel Otomasyon", layout="wide", page_icon="🛡️")

METRE_FIYATI = 70
MONTAJ_METRE_FIYATI = 100

if 'siparisler' not in st.session_state:
    st.session_state.siparisler = []

st.title("🛡️ Tel Montaj Sipariş Sistemi")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("👤 Müşteri Bilgileri")
    musteri = st.text_input("Müşteri Adı/Soyadı", placeholder="Örn: Ahmet Yılmaz")
    telefon = st.text_input("Telefon Numarası", placeholder="05xx xxx xx xx")
    
    st.subheader("📍 Teslimat Adresi")
    # SEÇMELİ DEĞİL, DİREKT YAZILABİLİR ALAN
    adres = st.text_area("Tam Adresiniz (İl, İlçe, Mahalle, Sokak...)", 
                         placeholder="Örn: Bursa, Nilüfer, Özlüce Mah. Çiçek Sk. No:4",
                         height=150)

with col2:
    st.subheader("📏 Hesaplama ve Onay")
    metre = st.number_input("Kaç Metre Tel Döşenecek?", min_value=0.0, step=1.0)
    montaj_istiyor_mu = st.radio("Montaj hizmeti istiyor musunuz? (Metresi 100 TL)", ("Evet", "Hayır"))
    
    malzeme_tutari = metre * METRE_FIYATI
    montaj_tutari = (metre * MONTAJ_METRE_FIYATI) if montaj_istiyor_mu == "Evet" else 0
    toplam = malzeme_tutari + montaj_tutari
    
    st.info(f"💰 **Toplam Tutar: {toplam} TL**")
    notlar = st.text_area("Sipariş Notu (Varsa)", placeholder="Örn: Bahçe kapısı sol taraftan başlanacak.")
    
    if st.button("SİPARİŞİ TAMAMLA", type="primary", use_container_width=True):
        if musteri and telefon and metre > 0 and adres:
            s_no = random.randint(10000, 99999)
            yeni = {
                "Sipariş No": s_no, 
                "Müşteri": musteri, 
                "Telefon": telefon,
                "Adres": adres,
                "Montaj": montaj_istiyor_mu, 
                "Metraj": f"{metre} m",
                "Toplam Tutar": f"{toplam} TL", 
                "Tarih": datetime.now().strftime('%d.%m.%Y %H:%M'),
                "Notlar": notlar
            }
            durum = mail_gonder(yeni)
            st.session_state.siparisler.append(yeni)
            
            if durum:
                st.success(f"Sipariş Alındı! No: #{s_no}")
                st.balloons()
            else:
                st.warning(f"Kayıt başarılı (No: #{s_no}) ancak mail gönderilemedi. Şifrenizi kontrol edin.")
        else:
            st.error("Lütfen Ad, Telefon, Adres ve Metre alanlarını boş bırakmayın!")

st.divider()
if st.session_state.siparisler:
    st.subheader("📑 Son Alınan Siparişler")
    st.dataframe(pd.DataFrame(st.session_state.siparisler))
