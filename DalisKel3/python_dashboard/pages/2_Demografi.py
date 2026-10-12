import plotly.express as px
import streamlit as st

import utils as u

u.setup("Demografi & Karakteristik Anak")
df = u.load()

a, b, c = st.columns(3)
a.plotly_chart(px.histogram(df, x="usia_anak_bulan", nbins=24, title="Sebaran usia (bulan)"))
b.plotly_chart(px.pie(df, names="jenis_kelamin", title="Jenis kelamin", hole=.4))
w = df.wilayah.fillna("(kosong)").value_counts().head(15).reset_index()
w.columns = ["wilayah", "jumlah"]
c.plotly_chart(px.bar(w, x="jumlah", y="wilayah", orientation="h", title="Jumlah anak per wilayah"))

st.subheader("Karakteristik keluarga")
a, b, c = st.columns(3)
for col, ttl, box in [("pendidikan_ibu", "Pendidikan ibu", a), ("pendapatan_keluarga", "Pendapatan keluarga", b),
                      ("pengasuh_utama", "Pengasuh utama", c)]:
    t = df[col].fillna("(kosong)").value_counts().reset_index()
    t.columns = [col, "jumlah"]
    box.plotly_chart(px.bar(t, x=col, y="jumlah", title=ttl), key=col)

st.subheader("Kesehatan & gizi")
a, b = st.columns(2)
t = df.groupby(["kelompok_usia", "status_gizi_bb_u"]).size().reset_index(name="jumlah")
a.plotly_chart(px.bar(t, x="kelompok_usia", y="jumlah", color="status_gizi_bb_u", title="Status gizi BB/U per kelompok usia",
                      category_orders={"kelompok_usia": u.URUT_USIA}))
b.plotly_chart(px.scatter(df, x="usia_kehamilan_minggu", y="berat_lahir_gram", color="kategori_kpsp",
                          color_discrete_map=u.WARNA, title="Usia kehamilan vs berat lahir"))
u.definisi()
