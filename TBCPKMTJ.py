import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import urllib.parse

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('hantam_tbc_v2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pasien (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT, usia INTEGER, bb INTEGER, no_wa TEXT,
                    kategori TEXT, dosis_fdc TEXT,
                    tgl_kunjungan TEXT, bulan_ke INTEGER, 
                    sisa_obat INTEGER, keluhan TEXT, 
                    status_medis TEXT, tgl_kembali TEXT, 
                    tgl_homecare TEXT)''')
    conn.commit()
    return conn

# --- LOGIKA DOSIS FDC (MEDIS) ---
def hitung_dosis(kategori, bb):
    if kategori == "Dewasa (FDC 4KDR)":
        if bb < 30: return "Konsultasi Spesialis (BB < 30kg)"
        elif 30 <= bb <= 37: return "2 Tablet FDC"
        elif 38 <= bb <= 54: return "3 Tablet FDC"
        elif 55 <= bb <= 70: return "4 Tablet FDC"
        else: return "5 Tablet FDC"
    else: # Kategori Anak (FDC Anak)
        if bb < 5: return "Konsultasi Spesialis (BB < 5kg)"
        elif 5 <= bb <= 7: return "1 Tablet FDC Anak"
        elif 8 <= bb <= 11: return "2 Tablet FDC Anak"
        elif 12 <= bb <= 14: return "3 Tablet FDC Anak"
        elif 15 <= bb <= 24: return "4 Tablet FDC Anak"
        else: return "Dosis Dewasa (BB > 24kg)"

# --- UI CONFIG ---
st.set_page_config(page_title="HANTAM TBC", page_icon="🥊", layout="wide")

# CSS untuk Vibe Gen Z (Glow, Rounded, Clean)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    .stButton>button { 
        background: linear-gradient(45deg, #ff416c, #ff4b2b); 
        color: white; border-radius: 12px; border: none; font-weight: bold;
        transition: 0.3s; box-shadow: 0 4px 15px rgba(255, 65, 108, 0.4);
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 65, 108, 0.6); }
    [data-testid="stForm"] { background: rgba(255, 255, 255, 0.05); border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("🥊 HANTAM TBC")
st.write("✨ *Slay the bacteria, save the community.* **Puskesmas Tirta Jaya Digital.**")

menu = ["🔥 Input Kunjungan", "📱 Monitoring & Tracking", "🏠 Homecare AI"]
choice = st.sidebar.selectbox("Pilih Aksi", menu)

if choice == "🔥 Input Kunjungan":
    st.markdown("### 📝 Patient Entry")
    with st.form("form_hantam", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            nama = st.text_input("Nama Pasien", placeholder="Nama lengkap...")
            no_wa = st.text_input("Nomor WA (62...)", placeholder="62812xxx")
        with c2:
            usia = st.number_input("Usia (Tahun)", min_value=0, max_value=120)
        with c3:
            bb = st.number_input("Berat Badan (Kg)", min_value=1)

        st.markdown("---")
        
        col_med1, col_med2 = st.columns(2)
        with col_med1:
            # Auto-Detection Kategori
            kategori = "Anak (FDC Anak)" if usia < 15 else "Dewasa (FDC 4KDR)"
            st.info(f"**Kategori Terdeteksi:** {kategori}")
            dosis = hitung_dosis(kategori, bb)
            st.warning(f"💊 **Rekomendasi Dosis:** {dosis}")
            
            bulan_ke = st.select_slider("Obat Bulan Ke-", options=list(range(1, 13)))
            sisa_obat = st.number_input("Sisa Obat (Butir)", 0)
        
        with col_med2:
            interval = st.radio("Jadwal Kembali", ["1 Bulan", "2 Minggu"], horizontal=True)
            medis = st.multiselect("Pemeriksaan", ["Cek HIV", "Cek GDS", "Rujukan Keluar"])
            keluhan = st.text_area("Keluhan / Side Effects", placeholder="Ada mual? Kesemutan?")

        # Tanggal Logika
        tgl_k = (datetime.now() + timedelta(days=30 if interval == "1 Bulan" else 14)).strftime("%d-%m-%Y")
        tgl_h = (datetime.now() + timedelta(days=15)).strftime("%d-%m-%Y")

        submit = st.form_submit_button("SIMPAN DATA & GENERATE JADWAL")

        if submit:
            conn = init_db()
            c = conn.cursor()
            c.execute('''INSERT INTO pasien (nama, usia, bb, no_wa, kategori, dosis_fdc, tgl_kunjungan, bulan_ke, sisa_obat, keluhan, status_medis, tgl_kembali, tgl_homecare)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                      (nama, usia, bb, no_wa, kategori, dosis, datetime.now().strftime("%d-%m-%Y"), bulan_ke, sisa_obat, keluhan, ", ".join(medis), tgl_k, tgl_h))
            conn.commit()
            st.balloons()
            st.success(f"🔥 Chill! Data {nama} sudah aman di database.")
            
            # WhatsApp Link
            msg = f"Halo {nama}, ini dari Puskesmas Tirta Jaya. Data pengobatan sudah masuk. BB: {bb}kg, Dosis: {dosis}. Jadwal kontrol berikutnya: *{tgl_k}*. Semangat sembuh!"
            wa_url = f"https://wa.me/{no_wa}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366; width:100%; height:50px; border-radius:10px; color:white; border:none; cursor:pointer;">📲 KIRIM PENGINGAT WA SEKARANG</button></a>', unsafe_allow_html=True)

elif choice == "📱 Monitoring & Tracking":
    st.markdown("### 📊 Database Pasien & Tracking")
    conn = init_db()
    df = pd.read_sql_query("SELECT * FROM pasien", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        # Export logic
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export ke Excel (CSV)", data=csv, file_name="hantam_tbc_data.csv")
    else:
        st.info("Belum ada data. Masukin dulu, Bestie!")

elif choice == "🏠 Homecare AI":
    st.markdown("### 🏠 Jadwal Kunjungan Rumah (Auto-AI)")
    conn = init_db()
    df = pd.read_sql_query("SELECT nama, no_wa, tgl_homecare, dosis_fdc FROM pasien", conn)
    if not df.empty:
        for i, row in df.iterrows():
            with st.expander(f"📍 {row['nama']} (Jadwal: {row['tgl_homecare']})"):
                st.write(f"Dosis yang dipantau: {row['dosis_fdc']}")
                wa_hc = f"https://wa.me/{row['no_wa']}?text=Halo {row['nama']}, petugas akan berkunjung ke rumah pada {row['tgl_homecare']} ya."
                st.markdown(f"[📲 Hubungi Pasien]({wa_hc})")
