import streamlit as st
from datetime import datetime
import pandas as pd
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GONDEREN_MAIL = "oefe02090@gmail.com"
ALICI_MAIL = "oefe02081@gmail.com"
SIFRE = "fmlftvqhyqyrkkhw"

def mail_gonder(siparis_detay):
    try:
        mesaj = MIMEMultipart()
        mesaj["From"] = GONDEREN_MAIL
        mesaj["To"] = ALICI_MAIL
        mesaj["Subject"] = f"YENİ SİPARİŞ #{siparis_detay['Sipariş No']} - {siparis_detay['Müşteri']}"
        icerik = f"Sipariş No: #{siparis_detay['Sipariş No']}\nMüşteri: {siparis_detay['Müşteri']}\nTelefon: {siparis_detay['Telefon']}\nMetraj: {siparis_detay['Metraj']}\nTutar: {siparis_detay['Toplam Tutar']}\nNotlar: {siparis_detay['Notlar']}"
        mesaj.attach(MIMEText(icerik, "plain"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GONDEREN_MAIL, SIFRE)
        server.sendmail(GONDEREN_MAIL, ALICI_MAIL, mesaj.as_string())
        server.quit()
        return True
    except:
        return False

st.set_page_config(page_title="Tel Montaj Otomasyonu", layout="wide")
MONTAJ_SABIT = 100
METRE_FIYATI = 70

if 'siparisler' not in st.session_state:
    st.session_state.siparisler = []

st.title("🛡️ Tel Montaj Sipariş Sistemi")
col1, col2 = st.columns([1, 1.5])

with col1:
    musteri = st.text_input("Müşteri Adı/Soyadı")
    telefon = st.text_input("Telefon Numaranız")
    metre = st.number_input("Kaç Metre?", min_value=0.0, step=1.0)
    toplam_tutar = (metre * METRE_FIYATI) + MONTAJ_SABIT
    st.subheader(f"Toplam: {toplam_tutar} TL")

with col2:
    notlar = st.text_area("Ek Notlar")
    if st.button("KAYDET VE ONAYLA"):
        if musteri and telefon and metre > 0:
            siparis_no = random.randint(10000, 99999)
            yeni = {"Sipariş No": siparis_no, "Müşteri": musteri, "Telefon": telefon, "Metraj": f"{metre} m", "Toplam Tutar": f"{toplam_tutar} TL", "Tarih": datetime.now().strftime('%d.%m.%Y %H:%M'), "Notlar": notlar}
            durum = mail_gonder(yeni)
            st.session_state.siparisler.append(yeni)
            if durum:
                st.success(f"Başarılı! No: #{siparis_no}")
                st.balloons()
            else:
                st.warning(f"Kaydedildi (No: #{siparis_no}) ama mail gitmedi.")
        else:
            st.error("Eksik alanları doldurun.")

st.divider()
if st.session_state.siparisler:
    st.table(pd.DataFrame(st.session_state.siparisler))
