import streamlit as st

import database as db
import utils as u

u.setup("Beranda")
df = u.load()

st.caption(f"Insight dari database aktif: `{db.get_engine().url.database}`")
st.subheader("Ringkasan")

risiko = df["kpsp_biner"] == "Berisiko"
kategori = df["kategori_kpsp"].value_counts(normalize=True)
terbanyak = kategori.index[0]
kelengkapan_rendah = int((df["kelengkapan_data"] < 80).sum())

a, b, c, d = st.columns(4)
a.metric("Anak dalam pilihan saat ini", len(df))
b.metric("Hasil berisiko", f"{risiko.mean() * 100:.1f}%")
c.metric("Kategori terbanyak", terbanyak, f"{kategori.iloc[0] * 100:.1f}% dari data")
d.metric("Kelengkapan di bawah 80%", kelengkapan_rendah)

if kelengkapan_rendah:
    st.info(
        f"Ada {kelengkapan_rendah} dari {len(df)} data dengan kelengkapan di bawah 80%. "
        "Periksa halaman Kualitas Data untuk melihat kolom yang sering kosong."
    )
else:
    st.success("Semua data pada pilihan saat ini memiliki kelengkapan minimal 80%.")

st.caption("Ringkasan deskriptif seluruh data pada database aktif, bukan diagnosis atau prediksi.")

st.subheader("Tujuan")
st.write(
    "Dashboard ini membantu merangkum hasil skrining perkembangan anak, "
    "mengeksplorasi karakteristik dan faktor yang berkaitan dengan kategori KPSP, "
    "serta memantau kualitas dan pengelolaan data."
)
st.info(
    "Analisis yang ditampilkan bersifat deskriptif atau asosiasi. Hasilnya tidak "
    "menetapkan diagnosis, tidak membuktikan sebab-akibat, dan bukan prediksi individual."
)
