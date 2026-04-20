import streamlit as st
from datetime import datetime
import pandas as pd
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ------------------ MAİL AYARLARI ------------------
# Buradaki bilgileri kendi mailin ve 16 haneli uygulama şifrenle doldur
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
        Tel Tutarı: {siparis_detay['Tel Tutarı']}
        Montaj Durumu: {siparis_detay['Montaj']}
        Montaj Tutarı: {siparis_detay['Montaj Tutarı']}
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

# ------------------ GÖRSEL AYARLAR (ARKA PLAN) ------------------
def arka_plan_ayarla():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.7)), 
                        url("https://depositphotos.com/tr/photo/razor-and-barbed-wire-fence-24938171.html");
            background-size: cover;
            background-attachment: fixed;
        }}
        /* Form alanlarını daha belirgin yapar */
        [data-testid="stVerticalBlock"] > div {{
            background-color: rgba(255, 255, 255, 0.85);
            padding: 15px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ------------------ SAYFA AYARLARI ------------------
st.set_page_config(page_title="Tel Otomasyon Sistemi", layout="wide", page_icon="🛡️")
arka_plan_ayarla()

METRE_FIYATI = 70
MONTAJ_METRE_FIYATI = 100

if 'siparisler' not in st.session_state:
    st.session_state.siparisler = []

# ------------------ ANA ARAYÜZ ------------------
st.title("🛡️ Tel Montaj Sipariş & Hesaplama Otomasyonu")
st.write(f"Güncel Birim Fiyatlar: Tel **{METRE_FIYATI} TL/m** | Montaj **{MONTAJ_METRE_FIYATI} TL/m**")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("👤 Müşteri Bilgileri")
    musteri = st.text_input("Ad Soyad", placeholder="Müşterinin adı")
    telefon = st.text_input("Telefon", placeholder="05xx xxx xx xx")
    
    st.subheader("📍 Teslimat Adresi")
    adres = st.text_area("Tam Adres (İl, İlçe, Mahalle, Sokak detaylı yazınız)", height=100)

with col2:
    st.subheader("📏 Hesaplama Ekranı")
    metre = st.number_input("Kaç Metre Tel Yapılacak?", min_value=0.0, step=1.0)
    montaj_secimi = st.radio("Montaj hizmeti dahil mi?", ("Evet", "Hayır"))
    
    # Hesaplamalar
    tel_bedeli = metre * METRE_FIYATI
    montaj_bedeli = (metre * MONTAJ_METRE_FIYATI) if montaj_secimi == "Evet" else 0
    genel_toplam = tel_bedeli + montaj_bedeli
    
    # Bilgi Paneli
    st.divider()
    st.write(f"🏗️ Tel Malzeme ({metre}m): **{tel_bedeli} TL**")
    st.write(f"🛠️ Montaj Hizmeti: **{montaj_bedeli} TL**")
    st.info(f"💰 **GENEL TOPLAM: {genel_toplam} TL**")
    
    notlar = st.text_area("Sipariş Notu (Özel istekler vb.)")
    
    if st.button("SİPARİŞİ ONAYLA VE GÖNDER", type="primary", use_container_width=True):
        if musteri and telefon and metre > 0 and adres:
            s_no = random.randint(10000, 99999)
            yeni_siparis = {
                "Sipariş No": s_no,
                "Müşteri": musteri,
                "Telefon": telefon,
                "Adres": adres,
                "Metraj": f"{metre} m",
                "Tel Tutarı": f"{tel_bedeli} TL",
                "Montaj": montaj_secimi,
                "Montaj Tutarı": f"{montaj_bedeli} TL",
                "Toplam Tutar": f"{genel_toplam} TL",
                "Tarih": datetime.now().strftime('%d.%m.%Y %H:%M'),
                "Notlar": notlar
            }
            
            mail_sonucu = mail_gonder(yeni_siparis)
            st.session_state.siparisler.append(yeni_siparis)
            
            if mail_sonucu:
                st.success(f"İşlem Başarılı! Sipariş Numaranız: #{s_no}")
                st.balloons()
            else:
                st.warning(f"Sipariş kaydedildi (ID: #{s_no}) fakat mail gönderilemedi. Lütfen uygulama şifresini kontrol edin.")
        else:
            st.error("Lütfen tüm alanları (Ad, Telefon, Adres ve Metre) eksiksiz doldurun!")

# ------------------ SİPARİŞ LİSTESİ ------------------
st.divider()
if st.session_state.siparisler:
    st.subheader("📑 Alınan Son Siparişler")
    st.dataframe(pd.DataFrame(st.session_state.siparisler))
