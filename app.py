import streamlit as st
import pandas as pd
from datetime import datetime
import zoneinfo
import os

# ==========================================
# 1. KONFIGURASI HALAMAN KHUSUS HP (MOBILE)
# ==========================================
st.set_page_config(
    page_title="Absensi Mobile",
    page_icon="📱",
    layout="centered", # Layout terpusat cocok untuk layar HP
    initial_sidebar_state="collapsed"
)

# Custom CSS Khusus Tampilan HP
st.markdown("""
<style>
    /* Google Font Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f1f5f9;
    }

    /* Hilangkan Padding Atas Berlebih */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 480px !important; /* Batas lebar layar HP */
    }

    /* Mobile Header Card */
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
        letter-spacing: -0.3px;
    }
    .mobile-subtitle {
        font-size: 12px;
        color: #94a3b8;
        margin-top: 4px;
    }

    /* Time Box Widget */
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
        font-size: 30px;
        font-weight: 800;
        color: #2563eb;
        line-height: 1.1;
    }
    .time-date {
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
        margin-top: 6px;
    }

    /* Custom Mobile Buttons */
    .stButton > button {
        border-radius: 14px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        height: 3.4rem !important;
        margin-bottom: 8px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }
</style>
""", unsafe_allow_html=True)

# Database File
DB_FILE = "absensi_log.csv"

if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["Tanggal", "Jam", "Nama", "Hari", "Status", "Menit_Telat"])
    df_init.to_csv(DB_FILE, index=False)

# Master Data Karyawan
EMPLOYEES = {
    "Arif": {"gapok": 4000000, "tunjangan": 1300000},
    "Budi Santoso": {"gapok": 3500000, "tunjangan": 1000000},
    "Siti Rahma": {"gapok": 3200000, "tunjangan": 800000}
}

# ==========================================
# 2. HEADER APP MOBILE
# ==========================================
st.markdown("""
<div class="mobile-header">
    <div class="mobile-title">📱 Presensi Karyawan</div>
    <div class="mobile-subtitle">Senin - Sabtu: 09.00 WIB | Minggu/Libur: Off</div>
</div>
""", unsafe_allow_html=True)

# Waktu WIB Real-Time
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

# Waktu Widget
st.markdown(f"""
<div class="time-card">
    <div class="time-clock">{jam_str} WIB</div>
    <div class="time-date">{hari_display}, {tanggal_str}</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. FORM ABSENSI (MOBILE OPTIMIZED)
# ==========================================
nama = st.selectbox("👤 Pilih Nama Karyawan:", list(EMPLOYEES.keys()))

st.write("**Tekan Tombol Status Kehadiran:**")

# Tombol Dibuat Menumpuk Vertikal (Sangat Nyaman di Layar HP)
btn_kerja = st.button("💼 Hari Kerja", type="primary", use_container_width=True)
btn_libur = st.button("🎉 Libur Kerja", use_container_width=True)
btn_absen = st.button("🚫 Tidak Masuk", use_container_width=True)

# LOGIKA HARI KERJA
if btn_kerja:
    jam_masuk_batas = now.replace(hour=9, minute=0, second=0, microsecond=0)
    menit_telat = 0
    if now > jam_masuk_batas:
        selisih = now - jam_masuk_batas
        menit_telat = int(selisih.total_seconds() // 60)
        
    df = pd.read_csv(DB_FILE)
    new_entry = pd.DataFrame([{
        "Tanggal": tanggal_str, "Jam": jam_str, "Nama": nama,
        "Hari": hari_display, "Status": "Hadir", "Menit_Telat": menit_telat
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    
    if menit_telat > 0:
        st.warning(f"⚠️ **Presensi Masuk!** {nama} jam {jam_str} WIB (Telat {menit_telat} Mnt).")
    else:
        st.success(f"🎉 **Presensi Berhasil!** {nama} hadir tepat waktu.")

# LOGIKA LIBUR KERJA
if btn_libur:
    df = pd.read_csv(DB_FILE)
    new_entry = pd.DataFrame([{
        "Tanggal": tanggal_str, "Jam": jam_str, "Nama": nama,
        "Hari": hari_display, "Status": "Libur", "Menit_Telat": 0
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.info(f"ℹ️ Status Libur dicatat untuk {nama}.")

# LOGIKA TIDAK MASUK
if btn_absen:
    df = pd.read_csv(DB_FILE)
    new_entry = pd.DataFrame([{
        "Tanggal": tanggal_str, "Jam": "-", "Nama": nama,
        "Hari": hari_display, "Status": "Tidak Masuk", "Menit_Telat": 0
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.error(f"🚨 Status Tidak Masuk dicatat untuk {nama}.")

st.markdown("---")

# ==========================================
# 4. PANEL ADMIN MOBILE
# ==========================================
with st.expander("🔑 Panel Admin (Rekap Gaji & Log)"):
    password = st.text_input("Password Admin:", type="password")
    
    if password == "admin123":
        st.success("Akses Admin Aktif.")
        df_log = pd.read_csv(DB_FILE)
        
        if not df_log.empty:
            st.write("### 💰 Rekap Gaji Bulan Ini")
            rekap_list = []
            for emp_name, emp_data in EMPLOYEES.items():
                emp_df = df_log[df_log["Nama"] == emp_name]
                
                total_hadir = len(emp_df[emp_df["Status"] == "Hadir"])
                total_alpa = len(emp_df[emp_df["Status"] == "Tidak Masuk"])
                total_telat_mnt = emp_df["Menit_Telat"].sum()
                
                denda_hari = len(emp_df[emp_df["Menit_Telat"] > 0]) if total_telat_mnt > 25 else 0
                pot_denda = denda_hari * 50000
                
                gapok = emp_data["gapok"]
                tunjangan = emp_data["tunjangan"]
                pot_absen = (gapok / 25) * total_alpa
                
                thp = (gapok + tunjangan) - pot_denda - pot_absen
                
                rekap_list.append({
                    "Nama": emp_name,
                    "Hadir": total_hadir,
                    "Alpa": total_alpa,
                    "Telat": f"{total_telat_mnt} mnt",
                    "Denda": f"Rp {pot_denda:,.0f}",
                    "THP": f"Rp {thp:,.0f}"
                })
                
            st.dataframe(pd.DataFrame(rekap_list), use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.write("### 🗑️ Hapus Baris Log")
            df_log["ID_Display"] = df_log.index.astype(str) + " - " + df_log["Nama"] + " [" + df_log["Status"] + "]"
            pilihan_hapus = st.selectbox("Pilih Data:", df_log["ID_Display"].tolist())
            
            if st.button("❌ Hapus Baris Terpilih", use_container_width=True):
                index_to_delete = int(pilihan_hapus.split(" - ")[0])
                df_log = df_log.drop(index=index_to_delete).drop(columns=["ID_Display"])
                df_log.to_csv(DB_FILE, index=False)
                st.success("Berhasil dihapus!")
                st.rerun()
        else:
            st.info("Belum ada data presensi.")
    elif password != "":
        st.error("Password Admin Salah!")
