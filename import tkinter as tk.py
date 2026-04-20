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
        
        SİPARİŞ ÖZETİ:
        Metraj: {siparis_detay['Metraj']}
        Tel Tutarı: {siparis_detay['Tel Tutarı']}  <-- BURASI EKLENDİ
        Montaj Durumu: {siparis_detay['Montaj']}
        Montaj Tutarı: {siparis_detay['Montaj Tutarı']} <-- BURASI EKLENDİ
        GENEL TOPLAM: {siparis_detay['Toplam Tutar']}
        
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

st.title("🛡️ Özgür Tel Montaj Sipariş Sistemi")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("👤 Müşteri Bilgileri")
    musteri = st.text_input("Müşteri Adı/Soyadı")
    telefon = st.text_input("Telefon Numarası")
    
    st.subheader("📍 Teslimat Adresi")
    adres = st.text_area("Tam Adresiniz (İl, İlçe, Mahalle...)", height=100)

with col2:
    st.subheader("📏 Hesaplama ve Onay")
    metre = st.number_input("Kaç Metre Tel Döşenecek?", min_value=0.0, step=1.0)
    montaj_istiyor_mu = st.radio("Montaj hizmeti istiyor musunuz? (Metresi 100 TL)", ("Evet", "Hayır"))
    
    # HESAPLAMALAR
    tel_tutari = metre * METRE_FIYATI
    montaj_tutari = (metre * MONTAJ_METRE_FIYATI) if montaj_istiyor_mu == "Evet" else 0
    genel_toplam = tel_tutari + montaj_tutari
    
    # EKRANDA GÖSTERİM (BURADA ARTIK TEL TUTARI GÖRÜNECEK)
    st.divider()
    st.write(f"📏 Tel Malzeme Tutarı ({metre}m x {METRE_FIYATI}TL): **{tel_tutari} TL**")
    st.write(f"🛠️ Toplam Montaj Bedeli: **{montaj_tutari} TL**")
    st.info(f"💰 **GENEL TOPLAM: {genel_toplam} TL**")
    
    notlar = st.text_area("Sipariş Notu")
    
    if st.button("SİPARİŞİ TAMAMLA", type="primary", use_container_width=True):
        if musteri and telefon and metre > 0 and adres:
            s_no = random.randint(10000, 99999)
            yeni = {
                "Sipariş No": s_no, 
                "Müşteri": musteri, 
                "Telefon": telefon,
                "Adres": adres,
                "Metraj": f"{metre} m",
                "Tel Tutarı": f"{tel_tutari} TL", # Veri kümesine eklendi
                "Montaj": montaj_istiyor_mu, 
                "Montaj Tutarı": f"{montaj_tutari} TL", # Veri kümesine eklendi
                "Toplam Tutar": f"{genel_toplam} TL", 
                "Tarih": datetime.now().strftime('%d.%m.%Y %H:%M'),
                "Notlar": notlar
            }
            durum = mail_gonder(yeni)
            st.session_state.siparisler.append(yeni)
            
            if durum:
                st.success(f"Sipariş Alındı! No: #{s_no}")
                st.balloons()
            else:
                st.warning(f"Kayıt başarılı (No: #{s_no}) ancak mail gönderilemedi.")
        else:
            st.error("Lütfen tüm alanları doldurun!")

st.divider()
if st.session_state.siparisler:
    st.subheader("📑 Son Siparişler")
    st.dataframe(pd.DataFrame(st.session_state.siparisler))
