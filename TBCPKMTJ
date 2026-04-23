import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import urllib.parse

# --- 1. KONFIGURASI DATABASE ---
def init_db():
    conn = sqlite3.connect('hantam_tbc.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pasien (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT, nik TEXT, no_wa TEXT,
                    tgl_kunjungan TEXT, bulan_ke INTEGER, 
                    sisa_obat INTEGER, keluhan TEXT, 
                    status_medis TEXT, tgl_kembali TEXT, 
                    tgl_homecare TEXT)''')
    conn.commit()
    return conn

# --- 2. FUNGSI LOGIKA ---
def simpan_data(nama, nik, wa, bulan, sisa, keluhan, medis, tgl_k, tgl_h):
    conn = init_db()
    c = conn.cursor()
    c.execute('''INSERT INTO pasien (nama, nik, no_wa, tgl_kunjungan, bulan_ke, sisa_obat, keluhan, status_medis, tgl_kembali, tgl_homecare)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
              (nama, nik, wa, datetime.now().strftime("%d-%m-%Y"), bulan, sisa, keluhan, medis, tgl_k, tgl_h))
    conn.commit()
    conn.close()

# --- 3. UI/UX MODERN ---
st.set_page_config(page_title="HANTAM TBC", page_icon="🏥", layout="wide")

# Custom CSS untuk tampilan modern
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #e74c3c; color: white; border: none; }
    .stButton>button:hover { background-color: #c0392b; color: white; }
    h1 { color: #2c3e50; font-family: 'Arial'; font-weight: 800; }
    .status-box { padding: 20px; border-radius: 10px; background-color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("🥊 HANTAM TBC")
st.subheader("Puskesmas Tirta Jaya - Sistem Monitoring Terintegrasi")
st.markdown("---")

menu = ["🆕 Input Kunjungan", "📊 Data & Tracking Pasien", "🏠 Jadwal Kunjungan Rumah"]
choice = st.sidebar.radio("Navigasi", menu)

if choice == "🆕 Input Kunjungan":
    st.markdown("### 📝 Form Kunjungan Pasien")
    
    with st.container():
        with st.form("form_tbc", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nama = st.text_input("Nama Lengkap Pasien", placeholder="Contoh: Budi Santoso")
                nik = st.text_input("NIK / No. Rekam Medis")
                no_wa = st.text_input("Nomor WhatsApp (Gunakan 62)", placeholder="628123456xxx")
                bulan_ke = st.select_slider("Obat Bulan Ke-", options=list(range(1, 13)))
                
            with col2:
                sisa_obat = st.number_input("Sisa Obat di Tangan (Butir)", min_value=0)
                interval = st.selectbox("Interval Jadwal Kembali", ["1 Bulan", "2 Minggu"])
                medis = st.multiselect("Pemeriksaan Medis", ["Cek HIV", "Cek GDS", "Rujukan Keluar"])
                keluhan = st.text_area("Keluhan & Efek Samping", placeholder="Tulis keluhan pasien di sini...")

            # Kalkulasi Tanggal Otomatis
            days = 30 if interval == "1 Bulan" else 14
            tgl_k = (datetime.now() + timedelta(days=days)).strftime("%d-%m-%Y")
            tgl_h = (datetime.now() + timedelta(days=15)).strftime("%d-%m-%Y") # AI-Suggested Homecare

            submitted = st.form_submit_button("SIMPAN DATA PENGOBATAN")
            
            if submitted:
                if nama and nik and no_wa:
                    simpan_data(nama, nik, no_wa, bulan_ke, sisa_obat, keluhan, ", ".join(medis), tgl_k, tgl_h)
                    st.success(f"✅ Data {nama} berhasil masuk sistem!")
                    
                    # Fitur WA Langsung
                    pesan = f"Halo {nama}, ini dari Puskesmas Tirta Jaya. Pengobatan TBC Anda bulan ke-{bulan_ke} telah dicatat. Jadwal kontrol kembali: *{tgl_k}*. Jangan lupa minum obat ya!"
                    encoded_msg = urllib.parse.quote(pesan)
                    wa_link = f"https://wa.me/{no_wa}?text={encoded_msg}"
                    
                    st.markdown(f"""
                        <div style="background-color:#d4edda; padding:15px; border-radius:10px;">
                            <p style="color:#155724;"><b>Jadwal Berikutnya: {tgl_k}</b></p>
                            <a href="{wa_link}" target="_blank">
                                <button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer;">
                                    📲 Kirim Pengingat WA ke Pasien
                                </button>
                            </a>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Mohon isi Nama, NIK, dan Nomor WA!")

elif choice == "📊 Data & Tracking Pasien":
    st.markdown("### 📋 Database Pasien & Tracking Obat")
    conn = init_db()
    df = pd.read_sql_query("SELECT * FROM pasien", conn)
    
    if not df.empty:
        # Penekanan pada tracking
        st.dataframe(df, use_container_width=True)
        
        # Tombol Export
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Database (Excel/CSV)", data=csv, file_name="database_hantam_tbc.csv", mime="text/csv")
    else:
        st.info("Belum ada data pasien.")

elif choice == "🏠 Jadwal Kunjungan Rumah":
    st.markdown("### 🏠 Jadwal Homecare Otomatis (AI Schedule)")
    conn = init_db()
    df = pd.read_sql_query("SELECT nama, no_wa, tgl_homecare, keluhan FROM pasien", conn)
    
    if not df.empty:
        st.write("Daftar pasien yang perlu dikunjungi petugas (H+15 setelah ambil obat):")
        for index, row in df.iterrows():
            with st.expander(f"📍 {row['nama']} - Jadwal: {row['tgl_homecare']}"):
                st.write(f"Catatan Keluhan: {row['keluhan']}")
                wa_hc = f"https://wa.me/{row['no_wa']}?text=Halo {row['nama']}, petugas Puskesmas Tirta Jaya akan melakukan kunjungan rumah rutin pada {row['tgl_homecare']}."
                st.markdown(f"[📲 Kirim Notif Kunjungan]({wa_hc})")
    else:
        st.info("Belum ada jadwal kunjungan rumah.")
