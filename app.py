import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Absensi & Gaji Otomatis", page_icon="📸", layout="centered")

# File Database Lokal
DB_FILE = "absensi_log.csv"

# Inisialisasi Database jika belum ada
if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["Tanggal", "Jam", "Nama", "Hari", "Status", "Menit_Telat"])
    df_init.to_csv(DB_FILE, index=False)

# Master Data Karyawan
EMPLOYEES = {
    "Arif": {"gapok": 4000000, "tunjangan": 1300000},
    "Budi Santoso": {"gapok": 3500000, "tunjangan": 1000000},
    "Siti Rahma": {"gapok": 3200000, "tunjangan": 800000}
}

st.title("📸 Presensi Karyawan Online")
st.caption("Jadwal: Senin-Jumat (09.00 - 17.30) | Sabtu (09.00 - 15.30)")

# ==========================================
# 1. FORM PRESENSI HARI AN (KARYAWAN)
# ==========================================
st.subheader("Form Absen Masuk")
nama = st.selectbox("Pilih Nama Karyawan:", list(EMPLOYEES.keys()))
camera_photo = st.camera_input("Ambil Foto Selfie Presensi")

if st.button("Submit Absen Masuk", type="primary"):
    if camera_photo is not None:
        now = datetime.now()
        tanggal_str = now.strftime("%Y-%m-%d")
        jam_str = now.strftime("%H:%M:%S")
        hari_num = now.weekday() # 0: Senin, 5: Sabtu, 6: Minggu
        
        menit_telat = 0
        status = "Hadir"
        
        if hari_num == 6:
            status = "Libur (Minggu)"
        else:
            jam_masuk_batas = now.replace(hour=9, minute=0, second=0, microsecond=0)
            if now > jam_masuk_batas:
                selisih = now - jam_masuk_batas
                menit_telat = int(selisih.total_seconds() // 60)

        # Simpan Data
        df = pd.read_csv(DB_FILE)
        new_entry = pd.DataFrame([{
            "Tanggal": tanggal_str,
            "Jam": jam_str,
            "Nama": nama,
            "Hari": now.strftime("%A"),
            "Status": status,
            "Menit_Telat": menit_telat
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(DB_FILE, index=False)
        
        st.success(f"✅ Absen Berhasil! Nama: {nama} | Jam: {jam_str} | Telat: {menit_telat} Menit")
    else:
        st.warning("⚠️ Harap ambil foto selfie terlebih dahulu!")

st.markdown("---")

# ==========================================
# 2. PANEL ADMIN (REKAP GAJI & FITUR HAPUS)
# ==========================================
with st.expander("🔑 Panel Admin / Pengelola (Hapus Absen & Cek Gaji)"):
    password = st.text_input("Masukkan Password Admin:", type="password")
    
    # Ganti password berikut sesuai keinginanmu
    if password == "admin123":
        st.success("Akses Admin Diberikan.")
        
        df_log = pd.read_csv(DB_FILE)
        
        if not df_log.empty:
            st.write("### 🗑️ Hapus Absen Salah")
            st.write("Pilih data absen yang ingin dihapus:")
            
            # Buat opsi daftar absen berdasarkan indeks baris
            df_log["ID_Display"] = df_log.index.astype(str) + " - " + df_log["Nama"] + " (" + df_log["Tanggal"] + " " + df_log["Jam"] + ")"
            pilihan_hapus = st.selectbox("Pilih Baris Absen untuk Dihapus:", df_log["ID_Display"].tolist())
            
            if st.button("❌ Hapus Absen Ini"):
                index_to_delete = int(pilihan_hapus.split(" - ")[0])
                df_log = df_log.drop(index=index_to_delete).drop(columns=["ID_Display"])
                df_log.to_csv(DB_FILE, index=False)
                st.success("Baris absen berhasil dihapus! Silakan lakukan re-fresh halaman.")
                st.rerun()

            st.markdown("---")
            st.write("### 📋 Log Presensi Keseluruhan")
            if "ID_Display" in df_log.columns:
                df_log = df_log.drop(columns=["ID_Display"])
            st.dataframe(df_log)
            
            # Rekapitulasi Gaji
            st.write("### 📊 Rekapitulasi Gaji Bulan Ini")
            rekap_list = []
            for emp_name, emp_data in EMPLOYEES.items():
                emp_df = df_log[df_log["Nama"] == emp_name]
                
                total_hadir = len(emp_df[emp_df["Status"] == "Hadir"])
                total_telat_mnt = emp_df["Menit_Telat"].sum()
                
                denda_hari = len(emp_df[emp_df["Menit_Telat"] > 0]) if total_telat_mnt > 25 else 0
                pot_denda = denda_hari * 50000
                
                gapok = emp_data["gapok"]
                tunjangan = emp_data["tunjangan"]
                thp = (gapok + tunjangan) - pot_denda
                
                rekap_list.append({
                    "Nama": emp_name,
                    "Hadir (Hari)": total_hadir,
                    "Total Telat (Menit)": total_telat_mnt,
                    "Denda Telat (Rp)": pot_denda,
                    "Gaji Pokok": gapok,
                    "Tunjangan": tunjangan,
                    "Take Home Pay (THP)": thp
                })
                
            st.dataframe(pd.DataFrame(rekap_list))
        else:
            st.info("Belum ada data presensi.")
    elif password != "":
        st.error("Password Admin Salah!")
