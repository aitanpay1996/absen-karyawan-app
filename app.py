import streamlit as st
import pandas as pd
from datetime import datetime
import zoneinfo
import os

# Set Layout Khusus Layar HP / Mobile
st.set_page_config(
    page_title="Absensi Arif",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Styling Tampilan HP
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc;
    }

    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 480px !important;
    }

    .mobile-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        padding: 20px 16px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .mobile-title {
        font-size: 20px;
        font-weight: 800;
        margin: 0;
    }
    .mobile-subtitle {
        font-size: 12px;
        color: #94a3b8;
        margin-top: 4px;
    }

    .time-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .time-clock {
        font-size: 32px;
        font-weight: 800;
        color: #2563eb;
    }
    .time-date {
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
        margin-top: 4px;
    }

    .stButton > button {
        border-radius: 14px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        height: 3.5rem !important;
        margin-bottom: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

DB_FILE = "absensi_log.csv"

if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["Tanggal", "Jam", "Nama", "Hari", "Status", "Menit_Telat"])
    df_init.to_csv(DB_FILE, index=False)

# Data Gaji Pokok & Tunjangan Arif
GAPOK = 4000000
TUNJANGAN = 1300000

# HEADER APP
st.markdown("""
<div class="mobile-header">
    <div class="mobile-title">📱 Presensi Arif</div>
    <div class="mobile-subtitle">Senin - Sabtu: 09.00 WIB | Minggu & Tanggal Merah: Off</div>
</div>
""", unsafe_allow_html=True)

# WAKTU REAL-TIME WIB
wib_tz = zoneinfo.ZoneInfo("Asia/Jakarta")
now = datetime.now(wib_tz)
tanggal_str = now.strftime("%Y-%m-%d")
jam_str = now.strftime("%H:%M:%S")
hari_name = now.strftime("%A")

hari_indo = {
    "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
    "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
}
hari_display = hari_indo.get(hari_name, hari_name)

st.markdown(f"""
<div class="time-card">
    <div class="time-clock">{jam_str} WIB</div>
    <div class="time-date">{hari_display}, {tanggal_str}</div>
</div>
""", unsafe_allow_html=True)

st.write("**Pilih Kehadiran Hari Ini:**")

btn_kerja = st.button("💼 Hari Kerja", type="primary", use_container_width=True)
btn_libur = st.button("🎉 Libur Kerja", use_container_width=True)
btn_absen = st.button("🚫 Tidak Masuk", use_container_width=True)

if btn_kerja:
    jam_masuk_batas = now.replace(hour=9, minute=0, second=0, microsecond=0)
    menit_telat = 0
    if now > jam_masuk_batas:
        selisih = now - jam_masuk_batas
        menit_telat = int(selisih.total_seconds() // 60)
        
    df = pd.read_csv(DB_FILE)
    new_entry = pd.DataFrame([{
        "Tanggal": tanggal_str, "Jam": jam_str, "Nama": "Arif",
        "Hari": hari_display, "Status": "Hadir", "Menit_Telat": menit_telat
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.success(f"✅ **Presensi Dicatat!** ({jam_str} WIB). Telat: {menit_telat} Mnt.")
    st.rerun()

if btn_libur:
    df = pd.read_csv(DB_FILE)
    new_entry = pd.DataFrame([{
        "Tanggal": tanggal_str, "Jam": jam_str, "Nama": "Arif",
        "Hari": hari_display, "Status": "Libur", "Menit_Telat": 0
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.info("ℹ️ Status Libur dicatat.")
    st.rerun()

if btn_absen:
    df = pd.read_csv(DB_FILE)
    new_entry = pd.DataFrame([{
        "Tanggal": tanggal_str, "Jam": "-", "Nama": "Arif",
        "Hari": hari_display, "Status": "Tidak Masuk", "Menit_Telat": 0
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.error("🚨 Status Tidak Masuk dicatat.")
    st.rerun()

st.markdown("---")

# ==========================================
# REKAP GAJI LANGSUNG TAMPIL
# ==========================================
st.subheader("📊 Rekap Gaji Bulan Ini")
df_log = pd.read_csv(DB_FILE)

if not df_log.empty:
    emp_df = df_log[df_log["Nama"] == "Arif"]
    
    total_hadir = len(emp_df[emp_df["Status"] == "Hadir"])
    total_alpa = len(emp_df[emp_df["Status"] == "Tidak Masuk"])
    total_telat_mnt = emp_df["Menit_Telat"].sum()
    
    # Denda Telat jika total akumulasi > 25 menit
    denda_hari = len(emp_df[emp_df["Menit_Telat"] > 0]) if total_telat_mnt > 25 else 0
    pot_denda = denda_hari * 50000
    
    # Potongan Absen = (Gapok / 25) * Total Alpa
    pot_absen = (GAPOK / 25) * total_alpa
    
    thp = (GAPOK + TUNJANGAN) - pot_denda - pot_absen
    
    st.markdown(f"""
    * **Hadir:** {total_hadir} Hari
    * **Tidak Masuk (Alpa):** {total_alpa} Hari
    * **Total Akumulasi Telat:** {total_telat_mnt} Menit
    * **Potongan Denda Telat:** Rp {pot_denda:,.0f}
    * **Potongan Tidak Masuk:** Rp {pot_absen:,.0f}
    * **Gaji Pokok:** Rp {GAPOK:,.0f}
    * **Tunjangan:** Rp {TUNJANGAN:,.0f}
    
    ### 💰 Take Home Pay (THP): **Rp {thp:,.0f}**
    """)

    st.markdown("---")
    st.subheader("📝 Kelola Log Absensi")
    
    # Hapus Absen Langsung Tanpa Password
    if "ID_Display" not in df_log.columns:
        df_log["ID_Display"] = df_log.index.astype(str) + " - " + df_log["Status"] + " (" + df_log["Tanggal"] + " " + df_log["Jam"] + ")"
        
    pilihan_hapus = st.selectbox("Pilih Baris Absen untuk Dihapus:", df_log["ID_Display"].tolist())
    
    if st.button("❌ Hapus Absen Ini", use_container_width=True):
        index_to_delete = int(pilihan_hapus.split(" - ")[0])
        df_log = df_log.drop(index=index_to_delete).drop(columns=["ID_Display"])
        df_log.to_csv(DB_FILE, index=False)
        st.success("Baris berhasil dihapus!")
        st.rerun()
else:
    st.info("Belum ada data presensi yang tercatat.")
