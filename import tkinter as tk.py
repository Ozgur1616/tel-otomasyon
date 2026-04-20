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
st.set_page_config(page_title="Tel Otomasyon", layout="wide")

METRE_FIYATI = 70
MONTAJ_UCRETI = 100

if 'siparisler' not in st.session_state:
    st.session_state.siparisler = []

st.title("🛡️ Tel Montaj Sipariş & Hesaplama Sistemi")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📋 Müşteri ve İş Bilgisi")
    musteri = st.text_input("Müşteri Adı/Soyadı")
    telefon = st.text_input("Telefon Numaranız")
    metre = st.number_input("Kaç Metre Tel?", min_value=0.0, step=1.0)
    
    # MONTAJ SEÇENEĞİ EKLEME
    montaj_istiyor_mu = st.radio("Montaj hizmeti istiyor musunuz?", ("Evet", "Hayır"))
    
    # Hesaplama
    malzeme_tutari = metre * METRE_FIYATI
    ek_ucret = MONTAJ_UCRETI if montaj_istiyor_mu == "Evet" else 0
    toplam_tutar = malzeme_tutari + ek_ucret
    
    st.divider()
    st.write(f"🏗️ Malzeme Tutarı: **{malzeme_tutari} TL**")
    st.write(f"🛠️ Montaj Bedeli: **{ek_ucret} TL**")
    st.subheader(f"💰 Toplam: {toplam_tutar} TL")

with col2:
    st.subheader("📤 Sipariş Kaydı")
    notlar = st.text_area("Ek Notlar")
    
    if st.button("SİPARİŞİ KAYDET VE ONAYLA", type="primary", use_container_width=True):
        if musteri and telefon and metre > 0:
            siparis_no = random.randint(10000, 99999)
            yeni_siparis = {
                "Sipariş No": siparis_no,
                "Müşteri": musteri,
                "Telefon": telefon,
                "Montaj Durumu": montaj_istiyor_mu,
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
                st.warning(f"Kaydedildi (#{siparis_no}) ama mail gitmedi. Şifreyi kontrol edin.")
        else:
            st.error("Lütfen Ad, Telefon ve Metre alanlarını doldurun.")

# ------------------ SİPARİŞ GEÇMİŞİ ------------------
st.divider()
if st.session_state.siparisler:
    st.table(pd.DataFrame(st.session_state.siparisler))
