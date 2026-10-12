import streamlit as st

import database as db

URUT = ["Sesuai", "Meragukan", "Kemungkinan Penyimpangan"]
WARNA = {"Sesuai": "#2ca02c", "Meragukan": "#ff7f0e", "Kemungkinan Penyimpangan": "#d62728"}
URUT_USIA = ["0-11 bln", "12-23 bln", "24-35 bln", "36-47 bln", "48-60 bln", "61-72 bln"]


@st.cache_resource
def _init():
    db.init_db()
    return True


def setup(judul: str):
    try:
        _init()
    except Exception as e:
        st.error(f"Gagal terhubung ke PostgreSQL. Periksa file .env dan pastikan database sudah dibuat.\n\n{e}")
        st.stop()
    st.title(judul)


def load():
    df = db.read_all()
    if df.empty:
        st.info("Belum ada data. Tambahkan lewat halaman Kelola Data, atau isi data contoh.")
        if st.button("Isi 150 data contoh"):
            db.seed_sample(150)
            st.rerun()
        st.stop()
    return df


def definisi():
    with st.expander("Definisi & cut-off (usulan, sepakati dengan tim)"):
        st.markdown("""
- **Kategori KPSP:** skor 9-10 = Sesuai, 7-8 = Meragukan, ≤6 = Kemungkinan penyimpangan. **Berisiko** = Meragukan + Penyimpangan.
- **Usia koreksi:** untuk anak prematur (<37 minggu) berusia ≤24 bulan, usia dikurangi selisih minggu menuju 40 minggu.
  Form KPSP dipilih dari usia koreksi.
- **Gadget:** <24 bulan: ada paparan layar = melebihi batas; ≥24 bulan: >60 menit/hari = melebihi batas (acuan WHO 2019).
- **Tidur cukup:** <12 bln 12-16 jam; 12-35 bln 11-14 jam; 36-60 bln 10-13 jam; >60 bln 9-12 jam.
- **Skor stimulasi (0-15):** 4 frekuensi stimulasi (Tidak pernah=0 … Sering=3) + skor durasi interaksi
  (<30 mnt=0, 30-59=1, 60-119=2, ≥120=3). Rendah ≤6, Sedang 7-10, Tinggi ≥11. Kosong bila ada komponen yang kosong.
- **Kelengkapan data:** % kolom input terisi. Kolom konten/pendampingan/tujuan gadget tidak dihitung bila anak tanpa gadget.
- **Catatan:** data cross-sectional, hasil menunjukkan **asosiasi**, bukan sebab-akibat.
""")
