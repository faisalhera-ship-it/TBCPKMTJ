import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import urllib.parse

# --- 1. LOGIKA DOSIS MEDIS (FDC) ---
def hitung_dosis_fdc(kategori, bb):
    if kategori == "Dewasa":
        if bb < 30: return "Konsultasi Spesialis (BB < 30kg)"
        elif 30 <= bb <= 37: return "2 Tablet FDC Dewasa"
        elif 38 <= bb <= 54: return "3 Tablet FDC Dewasa"
        elif 55 <= bb <= 70: return "4 Tablet FDC Dewasa"
        else: return "5 Tablet FDC Dewasa"
    else: # Anak
        if bb < 5: return "Konsultasi Spesialis (BB < 5kg)"
        elif 5 <= bb <= 7: return "1 Tablet FDC Anak"
        elif 8 <= bb <= 11: return "2 Tablet FDC Anak"
        elif 12 <= bb <= 16: return "3 Tablet FDC Anak"
        elif 17 <= bb <= 22: return "4 Tablet FDC Anak"
        elif 23 <= bb <= 30: return "5 Tablet FDC Anak"
        else: return "Gunakan Dosis Dewasa (BB > 30kg)"

# --- 2. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('hantam_tbc_pro.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pasien (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT, usia INTEGER, bb INTEGER, kategori TEXT,
                    no_wa TEXT, tgl_kunjungan TEXT, bulan_ke INTEGER, 
                    sisa_obat INTEGER, dosis TEXT, keluhan TEXT, 
                    medis TEXT, tgl_kembali TEXT, tgl_homecare TEXT)''')
    conn.commit()
    return conn

# --- 3. UI/UX CONFIGURATION ---
st.set_page_config(page_title="HANTAM TBC", page_icon="🥊", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; background-color: #FF4B4B; color: white; font-weight: bold; border: none; transition: 0.3s; }
    .stButton>button:hover { background-color: #ff3333; transform: scale(1.02); }
    .css-1r6slb0 { padding: 2rem; border-radius: 20px; background: #1e1e1e; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. MAIN APP ---
st.title("🥊 HANTAM TBC")
st.write("Sistem Monitoring & Keputusan Klinis Puskesmas Tirta Jaya")

menu = ["Input Kunjungan", "Dashboard & Tracking", "Jadwal Homecare"]
choice = st.sidebar.selectbox("Menu Utama", menu)

if choice == "Input Kunjungan":
    st.markdown("### 📝 Form Pemeriksaan & Dosis")
    
    with st.form("form_hantam", clear_on_submit=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            nama = st.text_input("Nama Lengkap Pasien", placeholder="Nama Pasien")
            no_wa = st.text_input("Nomor WhatsApp (628...)", placeholder="62812...")
        with col2:
            usia = st.number_input("Usia (Tahun)", min_value=0, max_value=120)
            kategori = "Anak" if usia < 15 else "Dewasa"
            st.info(f"Kategori: {kategori}")
        with col3:
            bb = st.number_input("Berat Badan (kg)", min_value=1)
        
        st.markdown("---")
        
        col4, col5 = st.columns(2)
        with col4:
            bulan_ke = st.slider("Pengobatan Bulan Ke-", 1, 12)
            sisa_obat = st.number_input("Sisa Obat Sebelumnya (Butir)", 0)
            medis = st.multiselect("Pemeriksaan", ["Cek HIV", "Cek GDS", "Rujukan Keluar"])
        
        with col5:
            interval = st.radio("Jadwal Kontrol Berikutnya", ["1 Bulan", "2 Minggu"], horizontal=True)
            keluhan = st.text_area("Keluhan & Efek Samping", placeholder="Input keluhan jika ada...")

        # Kalkulasi Otomatis
        dosis_final = hitung_dosis_fdc(kategori, bb)
        tgl_k = (datetime.now() + timedelta(days=30 if interval == "1 Bulan" else 14)).strftime("%d-%m-%Y")
        tgl_h = (datetime.now() + timedelta(days=15)).strftime("%d-%m-%Y")

        st.warning(f"💡 **Rekomendasi Dosis FDC:** {dosis_final}")

        if st.form_submit_button("SIMPAN DATA & CETAK DOSIS"):
            conn = init_db()
            c = conn.cursor()
            c.execute('''INSERT INTO pasien (nama, usia, bb, kategori, no_wa, tgl_kunjungan, bulan_ke, sisa_obat, dosis, keluhan, medis, tgl_kembali, tgl_homecare)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                      (nama, usia, bb, kategori, no_wa, datetime.now().strftime("%d-%m-%Y"), bulan_ke, sisa_obat, dosis_final, keluhan, ", ".join(medis), tgl_k, tgl_h))
            conn.commit()
            
            st.success(f"✅ Data {nama} Berhasil Disimpan!")
            
            # WhatsApp Trigger
            pesan = f"Halo {nama}, kunj
