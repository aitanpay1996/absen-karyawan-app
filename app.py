import streamlit as st
import pandas as pd
from datetime import datetime
import zoneinfo
import os

# ==========================================
# 1. KONFIGURASI HALAMAN & CUSTOM CSS MODERN
# ==========================================
st.set_page_config(
    page_title="Sistem Absensi & Payroll Online",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (CSS Injection)
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }

    /* Hero Banner / Header Style */
    .hero-banner {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #ffffff;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
    }
    .hero-title {
        font-size: 26px;
        font-weight: 700;
        margin: 0;
        color: #f8fafc;
    }
    .hero-subtitle {
        font-size: 14px;
        color: #94a3b8;
        margin-top: 4px;
    }

    /* Clock & Info Card */
    .info-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .clock-display {
        font-size: 32px;
        font-weight: 700;
        color: #2563eb;
        letter-spacing: -0.5px;
    }

    /* Button Styling Overrides */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        height: 3.2rem !important;
        font-size: 15px !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Database File Setup
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
# 2. HERO HEADER SECTION
# ==========================================
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">⚡ Portal Presensi & Payroll Karyawan</div>
    <div class="hero-subtitle">Jam Masuk Operasional: Senin – Sabtu (09.00 WIB) | Minggu & Libur Nasional: Off</div>
</div>
""", unsafe_allow_html=True)

# Waktu Real-Time WIB
wib_tz = zoneinfo.ZoneInfo("Asia/Jakarta")
now = datetime.now(wib_tz)
tanggal_str = now.strftime("%Y-%m-%d")
jam_str = now.strftime("%H:%M:%S")
hari_name = now.strftime("%A")

# Translation Hari
hari_indo = {
    "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
    "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
}
hari_display = hari_indo.get(hari_name, hari_name)

# Layout Grid Utama (Form Absen & Info Waktu)
col_main, col_sidebar = st.columns([2.2, 1], gap="medium")

# ==========================================
# 3. FORM PRESENSI (LEFT COLUMN)
# ==========================================
with col_main:
    st.subheader("📌 Form Absensi Harian")
    
    nama = st.selectbox("👤 Pilih Nama Karyawan:", list(EMPLOYEES.keys()))
    
    st.write("Silakan pilih status kehadiran Anda hari ini:")
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    btn_kerja = btn_col1.button("💼 Hari Kerja", type="primary", use_container_width=True)
    btn_libur = btn_col2.button("🎉 Libur Kerja", use_container_width=True)
    btn_absen = btn_col3.button("🚫 Tidak Masuk", use_container_width=True)

    # ACTION LOGIC: HARI KERJA
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
            st.warning(f"⚠️ **Presensi Dicatat!** {nama} hadir pukul {jam_str} WIB (Terlambat **{menit_telat} Menit**).")
        else:
            st.success(f"🎉 **Presensi Tepat Waktu!** {nama} hadir pukul {jam_str} WIB.")

    # ACTION LOGIC: LIBUR KERJA
    if btn_libur:
        df = pd.read_csv(DB_FILE)
        new_entry = pd.DataFrame([{
            "Tanggal": tanggal_str, "Jam": jam_str, "Nama": nama,
            "Hari": hari_display, "Status": "Libur", "Menit_Telat": 0
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(DB_FILE, index=False)
        st.info(f"ℹ️ Status Libur berhasil dicatat untuk **{nama}**.")

    # ACTION LOGIC: TIDAK MASUK
    if btn_absen:
        df = pd.read_csv(DB_FILE)
        new_entry = pd.DataFrame([{
            "Tanggal": tanggal_str, "Jam": "-", "Nama": nama,
            "Hari": hari_display, "Status": "Tidak Masuk", "Menit_Telat": 0
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(DB_FILE, index=False)
        st.error(f"🚨 Status **Tidak Masuk (Alpa)** dicatat untuk {nama}.")

# ==========================================
# 4. WAKTU & WIDGET INFO (RIGHT COLUMN)
# ==========================================
with col_sidebar:
    st.markdown(f"""
    <div class="info-card">
        <div style="font-size: 13px; color: #64748b; font-weight: 600; text-transform: uppercase;">Waktu Real-Time (WIB)</div>
        <div class="clock-display">{jam_str}</div>
        <div style="font-size: 14px; font-weight: 600; color: #334155; margin-top: 4px;">{hari_display}, {tanggal_str}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True)

# ==========================================
# 5. DASHBOARD ADMIN & REKAP GAJI
# ==========================================
with st.expander("🔑 Panel Administrator (Perhitungan Gaji & Kelola Absen)"):
    password = st.text_input("Masukkan Password Admin untuk Membuka:", type="password")
    
    if password == "admin123":
        st.success("🔓 Akses Administrator Diberikan.")
        df_log = pd.read_csv(DB_FILE)
        
        if not df_log.empty:
            tab_rekap, tab_kelola = st.tabs(["💰 Rekapitulasi Gaji Karyawan", "📝 Log Absensi & Hapus Data"])
            
            with tab_rekap:
                st.write("### 📊 Ringkasan Payroll Bulan Ini")
                rekap_list = []
                for emp_name, emp_data in EMPLOYEES.items():
                    emp_df = df_log[df_log["Nama"] == emp_name]
                    
                    total_hadir = len(emp_df[emp_df["Status"] == "Hadir"])
                    total_alpa = len(emp_df[emp_df["Status"] == "Tidak Masuk"])
                    total_telat_mnt = emp_df["Menit_Telat"].sum()
                    
                    # Denda Telat (>25 menit akumulasi)
                    denda_hari = len(emp_df[emp_df["Menit_Telat"] > 0]) if total_telat_mnt > 25 else 0
                    pot_denda = denda_hari * 50000
                    
                    # Potongan Tidak Masuk = (Gapok / 25) * Alpa
                    gapok = emp_data["gapok"]
                    tunjangan = emp_data["tunjangan"]
                    pot_absen = (gapok / 25) * total_alpa
                    
                    thp = (gapok + tunjangan) - pot_denda - pot_absen
                    
                    rekap_list.append({
                        "Nama Karyawan": emp_name,
                        "Hadir": total_hadir,
                        "Tidak Masuk": total_alpa,
                        "Total Telat (Mnt)": total_telat_mnt,
                        "Pot. Denda Telat": f"Rp {pot_denda:,.0f}",
                        "Pot. Tidak Masuk": f"Rp {pot_absen:,.0f}",
                        "Gaji Pokok": f"Rp {gapok:,.0f}",
                        "Tunjangan": f"Rp {tunjangan:,.0f}",
                        "Take Home Pay (THP)": f"Rp {thp:,.0f}"
                    })
                    
                st.dataframe(pd.DataFrame(rekap_list), use_container_width=True, hide_index=True)
                
            with tab_kelola:
                st.write("### 🗑️ Hapus / Koreksi Data Absensi")
                df_log["ID_Display"] = df_log.index.astype(str) + " - " + df_log["Nama"] + " [" + df_log["Status"] + "] (" + df_log["Tanggal"] + " " + df_log["Jam"] + ")"
                pilihan_hapus = st.selectbox("Pilih Baris yang Ingin Dihapus:", df_log["ID_Display"].tolist())
                
                if st.button("❌ Hapus Baris Terpilih", type="secondary"):
                    index_to_delete = int(pilihan_hapus.split(" - ")[0])
                    df_log = df_log.drop(index=index_to_delete).drop(columns=["ID_Display"])
                    df_log.to_csv(DB_FILE, index=False)
                    st.success("Data berhasil dihapus!")
                    st.rerun()
                
                st.markdown("---")
                st.write("### 📜 Seluruh Log Presensi")
                if "ID_Display" in df_log.columns:
                    df_log = df_log.drop(columns=["ID_Display"])
                st.dataframe(df_log, use_container_width=True)
        else:
            st.info("Belum ada data presensi yang tercatat.")
    elif password != "":
        st.error("Password Admin Salah!")
