import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import urllib.parse

# --- 1. LOGIKA DOSIS KLINIS (FDC) ---
def hitung_dosis(kategori, bb):
    if kategori == "Dewasa":
        if bb < 30: return "Konsultasi Spesialis (BB < 30kg)", 0
        elif 30 <= bb <= 37: return "2 Tablet FDC Dewasa", 2
        elif 38 <= bb <= 54: return "3 Tablet FDC Dewasa", 3
        elif 55 <= bb <= 70: return "4 Tablet FDC Dewasa", 4
        else: return "5 Tablet FDC Dewasa", 5
    else:  # Kategori Anak
        if bb < 5: return "Konsultasi Spesialis (BB < 5kg)", 0
        elif 5 <= bb <= 7: return "1 Tablet FDC Anak", 1
        elif 8 <= bb <= 11: return "2 Tablet FDC Anak", 2
        elif 12 <= bb <= 16: return "3 Tablet FDC Anak", 3
        elif 17 <= bb <= 22: return "4 Tablet FDC Anak", 4
        elif 23 <= bb <= 30: return "5 Tablet FDC Anak", 5
        else: return "Gunakan Dosis Dewasa (BB > 30kg)", 0

# --- 2. KONFIGURASI DATABASE ---
def init_db():
    conn = sqlite3.connect('hantam_tbc.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pasien (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT, usia INTEGER, bb INTEGER, 
                    nik TEXT, no_wa TEXT, tgl_kunjungan TEXT, 
                    bulan_ke INTEGER, sisa_obat INTEGER, 
                    dosis_harian TEXT, jml_obat_pulang INTEGER,
                    keluhan TEXT, status_medis TEXT, 
                    tgl_kembali TEXT, tgl_homecare TEXT)''')
    conn.commit()
    return conn

# --- 3. UI/UX "HANTAM TBC" ---
st.set_page_config(page_title="HANTAM TBC", page_icon="🥊", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 12px; background: linear-gradient(45deg, #FF4B2B, #FF416C); color: white; font-weight: bold; border: none; height: 3em; transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(255, 75, 43, 0.4); }
    .stTextInput>div>div>input, .stNumberInput>div>div>input { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🥊 HANTAM TBC")
st.write("### Puskesmas Tirta Jaya | Smart Monitoring & Automatic Dosage")
st.markdown("---")

menu = ["➕ Input Pasien & Obat", "🔍 Database & Tracking", "🏠 Jadwal Homecare AI"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "➕ Input Pasien & Obat":
    st.subheader("Data Kunjungan Pasien")
    
    with st.form("form_hantam", clear_on_submit=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            nama = st.text_input("Nama Lengkap")
            nik = st.text_input("NIK / No RM")
            no_wa = st.text_input("Nomor WhatsApp (628...)", help="Awali dengan 62")
        with col2:
            usia = st.number_input("Usia (Tahun)", min_value=0, max_value=120)
            bb = st.number_input("Berat Badan (kg)", min_value=0)
        with col3:
            kategori = "Anak" if usia < 15 else "Dewasa"
            st.info(f"Kategori: **{kategori}**")
            interval = st.selectbox("Interval Kembali", ["1 Bulan", "2 Minggu"])

        st.markdown("---")
        
        col_med1, col_med2 = st.columns(2)
        with col_med1:
            bulan_ke = st.number_input("Obat Bulan Ke-", 1, 12)
            sisa_obat = st.number_input("Sisa Obat (Butir)", 0)
            medis = st.multiselect("Pemeriksaan", ["Cek HIV", "Cek GDS", "Rujukan Keluar"])
        
        with col_med2:
            # Hitung Dosis Otomatis
            dosis_teks, jml_tab = hitung_dosis(kategori, bb)
            st.warning(f"**Rekomendasi Dosis:** {dosis_teks}")
            
            # Hitung Jumlah Obat Dibawa Pulang
            hari = 30 if interval == "1 Bulan" else 14
            obat_pulang = jml_tab * hari
            st.success(f"**Obat Dibawa Pulang:** {obat_pulang} Biji")
            
            keluhan = st.text_area("Input Keluhan/Efek Samping")

        # Kalkulasi Tanggal
        tgl_kembali = (datetime.now() + timedelta(days=hari)).strftime("%d-%m-%Y")
        tgl_homecare = (datetime.now() + timedelta(days=15)).strftime("%d-%m-%Y")

        if st.form_submit_button("SIMPAN DATA & CETAK JADWAL"):
            conn = init_db()
            c = conn.cursor()
            c.execute('''INSERT INTO pasien (nama, usia, bb, nik, no_wa, tgl_kunjungan, bulan_ke, sisa_obat, dosis_harian, jml_obat_pulang, keluhan, status_medis, tgl_kembali, tgl_homecare) 
                         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                      (nama, usia, bb, nik, no_wa, datetime.now().strftime("%d-%m-%Y"), bulan_ke, sisa_obat, dosis_teks, obat_pulang, keluhan, ", ".join(medis), tgl_kembali, tgl_homecare))
            conn.commit()
            
            st.balloons()
            st.success(f"Berhasil disimpan! Jadwal kembali: {tgl_kembali}")
            
            # WA Pengingat
            pesan = f"Halo {nama}, pengobatan TBC bulan ke-{bulan_ke} sudah tercatat di Puskesmas Tirta Jaya. Dosis Anda: {dosis_teks}. Obat dibawa pulang: {obat_pulang} biji. Jadwal kembali: *{tgl_kembali}*."
            wa_link = f"https://wa.me/{no_wa}?text={urllib.parse.quote(pesan)}"
            st.markdown(f'<a href="{wa_link}" target="_blank"><button style="background-color:#25D366; width:100%; color:white; border-radius:10px; border:none; padding:10px;">📲 KIRIM PENGINGAT WA SEKARANG</button></a>', unsafe_allow_html=True)

elif choice == "🔍 Database & Tracking":
    st.subheader("Monitoring Data Pasien (SQLite)")
    conn = init_db()
    df = pd.read_sql_query("SELECT * FROM pasien", conn)
    st.dataframe(df, use_container_width=True)
    
    # Download CSV sebagai backup ke Excel
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Export Database ke Excel/CSV", csv, "data_hantam_tbc.csv", "text/csv")

elif choice == "🏠 Jadwal Homecare AI":
    st.subheader("Jadwal Kunjungan Rumah Otomatis")
    conn = init_db()
    df = pd.read_sql_query("SELECT nama, no_wa, tgl_homecare, dosis_harian FROM pasien", conn)
    st.table(df)
