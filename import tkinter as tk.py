import streamlit as st
from datetime import datetime
import pandas as pd
import smtplib
import random
import requests # İl/İlçe verisini internetten çekmek için
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ------------------ MAİL AYARLARI ------------------
GONDEREN_MAIL = "oefe02081@gmail.com"
ALICI_MAIL = "oefe02090@gmail.com"
SIFRE = "fmlftvqhyqyrkkhw" 

# ------------------ TÜRKİYE TÜM İL & İLÇE VERİSİ ------------------
@st.cache_data # Veriyi her seferinde internetten çekmemesi için hafızaya alır
def illeri_getir():
    # Güvenilir bir kaynaktan Türkiye il-ilçe verisini çekiyoruz
    url = "https://raw.githubusercontent.com/fethisarihan/turkiye-iller-ilceler/master/iller-ilceler.json"
    try:
        response = requests.get(url)
        return response.json()
    except:
        # İnternet hatası olursa diye yedek basit liste
        return {"Bursa": ["Nilüfer", "Osmangazi"], "İstanbul": ["Beşiktaş", "Kadıköy"]}

data = illeri_getir()
iller = sorted([il["il"] for il in data])

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
        
        ADRES: {siparis_detay['Açık Adres']}
        KONUM: {siparis_detay['İlçe']} / {siparis_detay['İl']}
        
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
st.set_page_config(page_title="Tel Otomasyon - Türkiye", layout="wide")

METRE_FIYATI = 70
MONTAJ_METRE_FIYATI = 100

if 'siparisler' not in st.session_state:
    st.session_state.siparisler = []

st.title("🛡️ Tüm Türkiye Tel Montaj Otomasyonu")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("👤 Müşteri Bilgileri")
    musteri = st.text_input("Müşteri Adı/Soyadı")
    telefon = st.text_input("Telefon Numarası")
    
    st.subheader("📍 Adres Bilgileri")
    secilen_il = st.selectbox("İl Seçiniz", options=iller)
    
    # Seçilen ile göre ilçeleri filtreleme
    ilceler = []
    for il in data:
        if il["il"] == secilen_il:
            ilceler = sorted(il["ilceleri"])
            break
            
    secilen_ilce = st.selectbox("İlçe Seçiniz", options=ilceler)
    acik_adres = st.text_area("Cadde, Sokak, Kapı No", placeholder="Örn: Hürriyet Mah. Meşe Sk. No:12")

with col2:
    st.subheader("📏 Fiyatlandırma")
    metre = st.number_input("Kaç Metre Tel?", min_value=0.0, step=1.0)
    montaj_istiyor_mu = st.radio("Montaj hizmeti istiyor musunuz? (Metresi 100 TL)", ("Evet", "Hayır"))
    
    malzeme_tutari = metre * METRE_FIYATI
    montaj_tutari = (metre * MONTAJ_METRE_FIYATI) if montaj_istiyor_mu == "Evet" else 0
    toplam = malzeme_tutari + montaj_tutari
    
    st.info(f"💰 **Toplam Tutar: {toplam} TL**")
    notlar = st.text_area("Sipariş Notu")
    
    if st.button("SİPARİŞİ TAMAMLA", type="primary", use_container_width=True):
        if musteri and telefon and metre > 0 and acik_adres:
            s_no = random.randint(10000, 99999)
            yeni = {
                "Sipariş No": s_no, "Müşteri": musteri, "Telefon": telefon,
                "İl": secilen_il, "İlçe": secilen_ilce, "Açık Adres": acik_adres,
                "Montaj": montaj_istiyor_mu, "Metraj": f"{metre} m",
                "Toplam Tutar": f"{toplam} TL", "Tarih": datetime.now().strftime('%d.%m.%Y %H:%M'),
                "Notlar": notlar
            }
            durum = mail_gonder(yeni)
            st.session_state.siparisler.append(yeni)
            if durum:
                st.success(f"Sipariş Alındı! No: #{s_no}")
                st.balloons()
            else:
                st.warning("Kayıt yapıldı ama mail şifren hatalı olduğu için iletilemedi.")
        else:
            st.error("Lütfen eksik alan bırakmayın!")

st.divider()
if st.session_state.siparisler:
    st.subheader("📑 Alınan Siparişler")
    st.dataframe(pd.DataFrame(st.session_state.siparisler))
