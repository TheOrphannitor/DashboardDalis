import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import utils as u

u.setup("Analisis Faktor Risiko")
df = u.load()

hasil = st.radio("Definisi 'berisiko'", ["Meragukan + Kemungkinan penyimpangan", "Hanya kemungkinan penyimpangan"],
                 horizontal=True)
y = (df.kategori_kpsp != "Sesuai") if hasil.startswith("Meragukan") else (df.kategori_kpsp == "Kemungkinan Penyimpangan")
y = y.astype(int)
st.caption(f"Prevalensi berisiko: {y.mean() * 100:.1f}% dari {len(df)} anak")

# ---- Forest plot odds ratio ----
M = lambda col, d: df[col].map(d)
EXPO = {
    "Gadget melebihi batas usia": M("kelompok_durasi_gadget", {"Melebihi batas": 1, "Dalam batas": 0, "Tanpa layar": 0}),
    "Gadget tanpa pendampingan": M("pendampingan_gadget", {"Tidak pernah": 1, "Kadang": 0, "Selalu": 0}),
    "BBLR": M("kategori_bblr", {"BBLR": 1, "Normal": 0}),
    "Prematur": M("status_prematur", {"Prematur": 1, "Cukup bulan": 0}),
    "Tidur kurang": M("kategori_tidur", {"Kurang": 1, "Cukup": 0}),
    "Stimulasi rendah": M("kategori_stimulasi", {"Rendah": 1, "Sedang": 0, "Tinggi": 0}),
    "Posyandu tidak rutin": M("frekuensi_posyandu", {"Tidak pernah": 1, "Kadang": 1, "Rutin": 0}),
    "Tidak ikut PAUD": M("keikutsertaan_paud", {"Tidak": 1, "Ya": 0}),
    "Pendidikan ibu ≤ SMP": M("pendidikan_ibu", {"SD atau kurang": 1, "SMP": 1, "SMA": 0, "Perguruan tinggi": 0}),
    "Pendapatan < 1x UMK": M("pendapatan_keluarga", {"< 1x UMK": 1, "1-2x UMK": 0, "> 2x UMK": 0}),
    "Gizi kurang/buruk (BB/U)": M("status_gizi_bb_u", {"Gizi buruk": 1, "Gizi kurang": 1, "Gizi baik": 0, "Risiko gizi lebih": 0}),
    "Penyakit berulang": M("riwayat_penyakit_berulang", {"Ya": 1, "Tidak": 0}),
    "Gangguan pendengaran/penglihatan": M("riwayat_gangguan_pendengaran_penglihatan", {"Ya": 1, "Tidak": 0}),
    "Pernah konsultasi perkembangan (⚠ sebab-akibat terbalik)": M("riwayat_konsultasi_perkembangan", {"Ya": 1, "Tidak": 0}),
}


def odds_ratio(x, y):
    m = x.notna()
    x, y = x[m].astype(int), y[m].astype(int)
    a, b = int(((x == 1) & (y == 1)).sum()), int(((x == 1) & (y == 0)).sum())
    c, d = int(((x == 0) & (y == 1)).sum()), int(((x == 0) & (y == 0)).sum())
    if a + b == 0 or c + d == 0:
        return None
    n_exp, n_tot = a + b, len(x)
    if min(a, b, c, d) == 0:  # koreksi Haldane-Anscombe
        a, b, c, d = a + .5, b + .5, c + .5, d + .5
    o = a * d / (b * c)
    se = np.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return {"OR": o, "CI_bawah": np.exp(np.log(o) - 1.96 * se), "CI_atas": np.exp(np.log(o) + 1.96 * se),
            "n_terpapar": n_exp, "n_valid": n_tot}


rows = []
for k, x in EXPO.items():
    r = odds_ratio(x, y)
    if r:
        rows.append({"Faktor": k, **r})
st.subheader("Odds ratio mentah (unadjusted)")
if rows:
    t = pd.DataFrame(rows)
    t["plus"], t["minus"] = t.CI_atas - t.OR, t.OR - t.CI_bawah
    fig = px.scatter(t, x="OR", y="Faktor", log_x=True, error_x="plus", error_x_minus="minus",
                     hover_data=["n_terpapar", "n_valid"], title="OR (95% CI); garis putus-putus = tanpa asosiasi (OR=1)")
    fig.add_vline(x=1, line_dash="dash")
    st.plotly_chart(fig)
    st.dataframe(t[["Faktor", "OR", "CI_bawah", "CI_atas", "n_terpapar", "n_valid"]].round(2), hide_index=True)
    if len(df) < 100 or (t.n_terpapar < 10).any():
        st.warning("Sampel kecil / kelompok terpapar <10 pada beberapa faktor: CI lebar, tafsirkan hati-hati.")
else:
    st.info("Data belum cukup untuk menghitung odds ratio.")
st.caption("OR belum disesuaikan variabel lain (confounder) dan data bersifat cross-sectional: ini asosiasi, bukan sebab-akibat.")

# ---- Per faktor ----
st.subheader("Sebaran kategori KPSP per faktor")
FAKTOR = {
    "Kelompok durasi gadget": "kelompok_durasi_gadget", "Kategori tidur": "kategori_tidur",
    "Kategori stimulasi": "kategori_stimulasi", "Status BBLR": "kategori_bblr", "Status prematur": "status_prematur",
    "Status gizi BB/U": "status_gizi_bb_u", "Status gizi PB/TB/U": "status_gizi_pb_tb_u",
    "Pendidikan ibu": "pendidikan_ibu", "Pendapatan keluarga": "pendapatan_keluarga",
    "Pengasuh utama": "pengasuh_utama", "Ikut PAUD": "keikutsertaan_paud", "Frekuensi posyandu": "frekuensi_posyandu",
    "Jenis konten gadget": "jenis_konten_gadget", "Pendampingan gadget": "pendampingan_gadget",
    "Respons orang tua": "respons_orang_tua", "Frekuensi bermain tanpa layar": "frekuensi_bermain_tanpa_layar",
}
pilih = st.selectbox("Faktor", list(FAKTOR))
col = FAKTOR[pilih]
d = df.dropna(subset=[col])
a, b = st.columns(2)
a.plotly_chart(px.histogram(d, x=col, color="kategori_kpsp", barnorm="percent", text_auto=".0f",
                            color_discrete_map=u.WARNA, category_orders={"kategori_kpsp": u.URUT},
                            title="Proporsi (%) per kategori"), key="prop")
ct = pd.crosstab(d[col], d["kategori_kpsp"]).reindex(columns=u.URUT, fill_value=0)
ct["Total"] = ct.sum(axis=1)
ct["% berisiko"] = ((ct["Meragukan"] + ct["Kemungkinan Penyimpangan"]) / ct["Total"] * 100).round(1)
b.write("Tabel silang (jumlah)")
b.dataframe(ct)
if (ct["Total"] < 10).any():
    b.warning("Ada kategori dengan n < 10, persentasenya tidak stabil.")

# ---- Korelasi ----
st.subheader("Korelasi Spearman dengan skor KPSP")
num = ["usia_anak_bulan", "durasi_gadget_menit", "durasi_tidur_jam", "durasi_interaksi_menit", "skor_stimulasi",
       "berat_lahir_gram", "usia_kehamilan_minggu", "jumlah_saudara", "jumlah_anggota_rumah",
       "durasi_pengasuhan_jam", "berat_badan_kg", "tinggi_panjang_badan_cm"]
cr = df[num + ["skor_kpsp"]].astype(float).corr(method="spearman")["skor_kpsp"].drop("skor_kpsp").dropna()
if len(cr):
    cr = cr.sort_values().reset_index()
    cr.columns = ["variabel", "rho"]
    st.plotly_chart(px.bar(cr, x="rho", y="variabel", orientation="h", range_x=[-1, 1]))
u.definisi()
