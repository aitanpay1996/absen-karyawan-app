import streamlit as st
import pandas as pd
from datetime import datetime
import zoneinfo
import os

# ==========================================
# KONFIGURASI HALAMAN & TEMA MODERN
# ==========================================
st.set_page_config(page_title="Dashboard Presensi & Gaji", page_icon="💼", layout="wide")

# Custom CSS untuk tampilan premium & bersih
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
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

# Header Aplikasi
st.title("💼 Dashboard Presensi & Karyawan")
st.caption("🕒 Jam Masuk Operasional: Senin - Sabtu (09.00 WIB) | Minggu & Tanggal Merah: Libur")
st.markdown("---")

# ==========================================
# 1. PANEL ABSENSI (KARYAWAN)
# ==========================================
col_form, col_info = st.columns([2, 1])

with col_form:
    st.subheader("📌 Form Presensi Harian")
    nama = st.selectbox("Pilih Nama Karyawan:", list(EMPLOYEES.keys()))
    
    st.write("Pilih Status Kehadiran Hari Ini:")
    c1, c2, c3 = st.columns(3)
    
    btn_kerja = c1.button("💼 Hari Kerja", type="primary")
    btn_libur = c2.button("🎉 Libur Kerja")
    btn_absen = c3.button("🚫 Tidak Masuk")

    # Waktu Real-Time WIB (Asia/Jakarta)
    wib_tz = zoneinfo.ZoneInfo("Asia/Jakarta")
    now = datetime.now(wib_tz)
    tanggal_str = now.strftime("%Y-%m-%d")
    jam_str = now.strftime("%H:%M:%S")
    hari_name = now.strftime("%A")

    # LOGIKA TOMBOL HARI KERJA
    if btn_kerja:
        jam_masuk_batas = now.replace(hour=9, minute=0, second=0, microsecond=0)
        menit_telat = 0
        if now > jam_masuk_batas:
            selisih = now - jam_masuk_batas
            menit_telat = int(selisih.total_seconds() // 60)
            
        df = pd.read_csv(DB_FILE)
        new_entry = pd.DataFrame([{
            "Tanggal": tanggal_str, "Jam": jam_str, "Nama": nama,
            "Hari": hari_name, "Status": "Hadir", "Menit_Telat": menit_telat
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(DB_FILE, index=False)
        
        if menit_telat > 0:
            st.warning(f"✅ Presensi Hadir Diterima! {nama} pada jam {jam_str} WIB (Terlambat {menit_telat} Menit).")
        else:
            st.success(f"✅ Presensi Hadir Tepat Waktu! {nama} pada jam {jam_str} WIB.")

    # LOGIKA TOMBOL LIBUR KERJA
    if btn_libur:
        df = pd.read_csv(DB_FILE)
        new_entry = pd.DataFrame([{
            "Tanggal": tanggal_str, "Jam": jam_str, "Nama": nama,
            "Hari": hari_name, "Status": "Libur", "Menit_Telat": 0
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(DB_FILE, index=False)
        st.info(f"ℹ️ Status Libur berhasil dicatat untuk {nama}.")

    # LOGIKA TOMBOL TIDAK MASUK
    if btn_absen:
        df = pd.read_csv(DB_FILE)
        new_entry = pd.DataFrame([{
            "Tanggal": tanggal_str, "Jam": "-", "Nama": nama,
            "Hari": hari_name, "Status": "Tidak Masuk", "Menit_Telat": 0
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(DB_FILE, index=False)
        st.error(f"⚠️ Status Tidak Masuk (Alpa) dicatat untuk {nama}.")

with col_info:
    st.subheader("ℹ️ Informasi Sistem")
    st.markdown(f"""
    <div class="metric-card">
        <h4>Waktu Saat Ini (WIB)</h4>
        <h2 style="color: #1F4E79;">{jam_str}</h2>
        <p>{hari_name}, {tanggal_str}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 2. PANEL ADMIN & REKAP GAJI
# ==========================================
with st.expander("🔑 Panel Admin / Pengelola (Cek Gaji & Hapus Absen)"):
    password = st.text_input("Masukkan Password Admin:", type="password")
    
    if password == "admin123":
        st.success("Akses Admin Aktif.")
        df_log = pd.read_csv(DB_FILE)
        
        if not df_log.empty:
            tab1, tab2 = st.tabs(["📊 Rekapitulasi Gaji", "🗑️ Kelola Log Presensi"])
            
            with tab1:
                st.write("### 💰 Perhitungan Gaji & Potongan Bulan Ini")
                rekap_list = []
                for emp_name, emp_data in EMPLOYEES.items():
                    emp_df = df_log[df_log["Nama"] == emp_name]
                    
                    total_hadir = len(emp_df[emp_df["Status"] == "Hadir"])
                    total_alpa = len(emp_df[emp_df["Status"] == "Tidak Masuk"])
                    total_telat_mnt = emp_df["Menit_Telat"].sum()
                    
                    # Logika Denda Telat (>25 Menit)
                    denda_hari = len(emp_df[emp_df["Menit_Telat"] > 0]) if total_telat_mnt > 25 else 0
                    pot_denda = denda_hari * 50000
                    
                    # Potongan Absen = (Gapok / 25 Hari Kerja) * Jumlah Alpa
                    gapok = emp_data["gapok"]
                    tunjangan = emp_data["tunjangan"]
                    pot_absen = (gapok / 25) * total_alpa
                    
                    thp = (gapok + tunjangan) - pot_denda - pot_absen
                    
                    rekap_list.append({
                        "Nama": emp_name,
                        "Hadir": total_hadir,
                        "Tidak Masuk": total_alpa,
                        "Total Telat (Mnt)": total_telat_mnt,
                        "Pot. Denda Telat": f"Rp {pot_denda:,.0f}",
                        "Pot. Tidak Masuk": f"Rp {pot_absen:,.0f}",
                        "Gaji Pokok": f"Rp {gapok:,.0f}",
                        "Tunjangan": f"Rp {tunjangan:,.0f}",
                        "Take Home Pay (THP)": f"Rp {thp:,.0f}"
                    })
                    
                st.dataframe(pd.DataFrame(rekap_list), use_container_width=True)
                
            with tab2:
                st.write("### 📋 Log Presensi & Hapus Data")
                df_log["ID_Display"] = df_log.index.astype(str) + " - " + df_log["Nama"] + " [" + df_log["Status"] + "] (" + df_log["Tanggal"] + " " + df_log["Jam"] + ")"
                pilihan_hapus = st.selectbox("Pilih Baris untuk Dihapus:", df_log["ID_Display"].tolist())
                
                if st.button("❌ Hapus Baris Terpilih"):
                    index_to_delete = int(pilihan_hapus.split(" - ")[0])
                    df_log = df_log.drop(index=index_to_delete).drop(columns=["ID_Display"])
                    df_log.to_csv(DB_FILE, index=False)
                    st.success("Data berhasil dihapus!")
                    st.rerun()
                
                st.markdown("---")
                if "ID_Display" in df_log.columns:
                    df_log = df_log.drop(columns=["ID_Display"])
                st.dataframe(df_log, use_container_width=True)
        else:
            st.info("Belum ada data presensi yang tercatat.")
    elif password != "":
        st.error("Password Admin Salah!")
