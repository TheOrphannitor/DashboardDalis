import pandas as pd
import plotly.express as px
import streamlit as st

import utils as u
from schema import NAMES, GADGET_COND

u.setup("Kualitas Data & Beban Petugas")
df = u.load()

m = df.kelengkapan_data
a, b, c = st.columns(3)
a.metric("Rata-rata kelengkapan", f"{m.mean():.1f}%")
b.metric("Data lengkap 100%", f"{(m >= 100).mean() * 100:.1f}%")
c.metric("Data < 80% lengkap", int((m < 80).sum()))

a, b = st.columns(2)
a.plotly_chart(px.histogram(df, x="kelengkapan_data", nbins=20, title="Distribusi kelengkapan data (%)"))
inp = [n for n in NAMES if n not in GADGET_COND]
ms = (df[inp].isna().mean() * 100).sort_values().reset_index()
ms.columns = ["kolom", "persen_kosong"]
b.plotly_chart(px.bar(ms[ms.persen_kosong > 0].tail(20), x="persen_kosong", y="kolom", orientation="h",
                      title="Persentase nilai kosong per kolom"))

st.subheader("Beban & pola per petugas")
p = df.groupby("petugas_skrining").agg(
    jumlah=("id_anak", "count"), rata_skor=("skor_kpsp", "mean"),
    pct_berisiko=("kpsp_biner", lambda s: (s == "Berisiko").mean() * 100),
    kelengkapan=("kelengkapan_data", "mean")).round(1).reset_index()
a, b = st.columns(2)
a.dataframe(p, hide_index=True)
b.plotly_chart(px.box(df, x="petugas_skrining", y="skor_kpsp", title="Sebaran skor KPSP per petugas"))
st.caption("Perbedaan pola skor antar petugas yang mencolok dapat menandakan perbedaan cara penilaian (bukan perbedaan anak).")

st.subheader("Pemeriksaan konsistensi")
cek = {
    "Tidur + interaksi + gadget > 24 jam": (df.durasi_tidur_jam + (df.durasi_interaksi_menit + df.durasi_gadget_menit) / 60) > 24,
    "Prematur (<37 mgg) tetapi berat lahir > 4000 g": (df.usia_kehamilan_minggu < 37) & (df.berat_lahir_gram > 4000),
    "Usia < 3 bulan (form KPSP tidak tersedia)": df.form_kpsp == "Di bawah 3 bln",
    "Tanggal skrining di masa depan": df.tanggal_skrining > pd.Timestamp.today().normalize(),
    "Durasi pengasuhan + tidur > 24 jam": (df.durasi_pengasuhan_jam + df.durasi_tidur_jam) > 24,
}
ring = pd.DataFrame({"Aturan": list(cek), "Jumlah baris": [int(v.fillna(False).sum()) for v in cek.values()]})
st.dataframe(ring, hide_index=True)
pilih = st.selectbox("Lihat baris yang bermasalah", ["(tidak ada)"] + list(cek))
if pilih != "(tidak ada)":
    st.dataframe(df[cek[pilih].fillna(False)][["id_anak", "tanggal_skrining", "usia_anak_bulan", "petugas_skrining"]],
                 hide_index=True)
