import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Absensi & Gaji Otomatis", page_icon="📸", layout="centered")

# File Database Lokal
DB_FILE = "absensi_log.csv"

# Inisialisasi Database
if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["Tanggal", "Jam", "Nama", "Hari", "Status", "Menit_Telat"])
    df_init.to_csv(DB_FILE, index=False)

# Master Data Karyawan (Bisa ditambah/ubah)
EMPLOYEES = {
    "Arif": {"gapok": 4000000, "tunjangan": 1300000},
    "Budi Santoso": {"gapok": 3500000, "tunjangan": 1000000},
    "Siti Rahma": {"gapok": 3200000, "tunjangan": 800000}
}

st.title("📸 Presensi Karyawan Online")
st.caption("Jadwal: Senin-Jumat (09.00 - 17.30) | Sabtu (09.00 - 15.30)")

# Form Absensi
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
        
        # Logika Jam Kerja (Minggu / Libur)
        if hari_num == 6:
            status = "Libur (Minggu)"
        else:
            # Toleransi Jam Masuk 09:00:00
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
        st.warning("⚠️ Harap ambil foto selfie terlebih dahulu sebelum klik submit!")

st.markdown("---")

# Dashboard Admin / Rekapitulasi Gaji
with st.expander("📊 Lihat Rekapitulasi Gaji & Absensi (Admin)"):
    df_log = pd.read_csv(DB_FILE)
    if not df_log.empty:
        st.write("### Data Log Presensi Real-Time")
        st.dataframe(df_log)
        
        # Hitung Ringkasan Per Karyawan
        st.write("### Rekapitulasi Gaji Bulan Ini")
        rekap_list = []
        for emp_name, emp_data in EMPLOYEES.items():
            emp_df = df_log[df_log["Nama"] == emp_name]
            
            total_hadir = len(emp_df[emp_df["Status"] == "Hadir"])
            total_telat_mnt = emp_df["Menit_Telat"].sum()
            
            # Logika Denda: Jika akumulasi telat > 25 menit
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
        st.info("Belum ada data presensi yang masuk.")