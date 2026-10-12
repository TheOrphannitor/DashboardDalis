import plotly.express as px
import streamlit as st

import utils as u

u.setup("Dashboard Developmental Delay pada Anak")
df = u.load()

pct = lambda m: f"{m.mean() * 100:.1f}%"
c = st.columns(6)
c[0].metric("Total anak", len(df))
c[1].metric("Sesuai", pct(df.kategori_kpsp == "Sesuai"))
c[2].metric("Meragukan", pct(df.kategori_kpsp == "Meragukan"))
c[3].metric("Kemungkinan penyimpangan", pct(df.kategori_kpsp == "Kemungkinan Penyimpangan"))
c[4].metric("BBLR", pct(df.kategori_bblr == "BBLR"))
g = df.kelompok_durasi_gadget.dropna()
c[5].metric("Gadget melebihi batas", pct(g == "Melebihi batas") if len(g) else "-")
st.caption(f"Rata-rata kelengkapan data: {df.kelengkapan_data.mean():.1f}%")

a, b = st.columns(2)
a.plotly_chart(px.pie(df, names="kategori_kpsp", hole=.4, title="Distribusi kategori KPSP",
                      color="kategori_kpsp", color_discrete_map=u.WARNA,
                      category_orders={"kategori_kpsp": u.URUT}))
t = df.groupby(["kelompok_usia", "kategori_kpsp"]).size().reset_index(name="jumlah")
b.plotly_chart(px.bar(t, x="kelompok_usia", y="jumlah", color="kategori_kpsp", title="Kategori KPSP per kelompok usia",
                      color_discrete_map=u.WARNA, category_orders={"kategori_kpsp": u.URUT, "kelompok_usia": u.URUT_USIA}))

a, b = st.columns(2)
df["bulan"] = df.tanggal_skrining.dt.to_period("M").astype(str)
t = df.groupby(["bulan", "kategori_kpsp"]).size().reset_index(name="jumlah")
a.plotly_chart(px.bar(t, x="bulan", y="jumlah", color="kategori_kpsp", title="Tren skrining per bulan",
                      color_discrete_map=u.WARNA, category_orders={"kategori_kpsp": u.URUT}))
t = df.tindak_lanjut_kpsp.value_counts().reset_index()
t.columns = ["tindak_lanjut", "jumlah"]
b.plotly_chart(px.bar(t, x="jumlah", y="tindak_lanjut", orientation="h", title="Tindak lanjut yang diperlukan"))

u.definisi()
