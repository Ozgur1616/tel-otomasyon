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
        Montaj Durumu: {siparis_detay['Montaj Durumu']}
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

# BİRİM FİYATLAR
METRE_FIYATI = 70
MONTAJ_METRE_FIYATI = 100 # Montaj bedeli artık metre başına 100 TL

if 'siparisler' not in st.session_state:
    st.session_state.siparisler = []

st.title("🛡️ Tel Montaj Sipariş & Hesaplama Sistemi")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📋 Müşteri ve İş Bilgisi")
    musteri = st.text_input("Müşteri Adı/Soyadı", placeholder="Özgür ...")
    telefon = st.text_input("Telefon Numaranız", placeholder="05xx...")
    metre = st.number_input("Kaç Metre Tel?", min_value=0.0, step=1.0)
    
    montaj_istiyor_mu = st.radio("Montaj hizmeti istiyor musunuz? (Metresi 100 TL)", ("Evet", "Hayır"))
    
    # HESAPLAMA MANTIĞI
    malzeme_tutari = metre * METRE_FIYATI
    # Eğer montaj istenirse: metre x 100 TL, istenmezse 0 TL
    toplam_montaj_bedeli = (metre * MONTAJ_METRE_FIYATI) if montaj_istiyor_mu == "Evet" else 0
    toplam_tutar = malzeme_tutari + toplam_montaj_bedeli
    
    st.divider()
    st.write(f"🏗️ Malzeme Tutarı ({metre}m x {METRE_FIYATI}TL): **{malzeme_tutari} TL**")
    st.write(f"🛠️ Toplam Montaj Bedeli: **{toplam_montaj_bedeli} TL**")
    st.subheader(f"💰 GENEL TOPLAM: {toplam_tutar} TL")

with col2:
    st.subheader("📤 Sipariş Kaydı")
    notlar = st.text_area("Ek Notlar (Adres vb.)")
    
    if st.button("SİPARİŞİ KAYDET VE ONAYLA", type="primary", use_container_width=True):
        if musteri and telefon and metre > 0:
            siparis_no = random.randint(10000, 99999)
            yeni_siparis = {
                "Sipariş No": siparis_no,
                "Müşteri": musteri,
                "Telefon": telefon,
                "Montaj": montaj_istiyor_mu,
                "Metraj": f"{metre} m",
                "Toplam Tutar": f"{toplam_tutar} TL",
                "Tarih": datetime.now().strftime('%d.%m.%Y %H:%M'),
                "Notlar": notlar
            }
            
            durum = mail_gonder(yeni_siparis)
            st.session_state.siparisler.append(yeni_siparis)
            
            if durum:
                st.success(f"Başarılı! Sipariş No: #{siparis_no}")
                st.balloons()
            else:
                st.warning(f"Kaydedildi (#{siparis_no}) ama mail gitmedi. Gmail uygulama şifresini kontrol edin.")
        else:
            st.error("Lütfen Ad, Telefon ve Metre alanlarını doldurun.")

# ------------------ SİPARİŞ GEÇMİŞİ ------------------
st.divider()
st.subheader("📑 Alınan Siparişler Listesi")
if st.session_state.siparisler:
    df = pd.DataFrame(st.session_state.siparisler)
    st.table(df)
