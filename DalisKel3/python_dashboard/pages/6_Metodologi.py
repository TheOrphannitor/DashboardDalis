import streamlit as st

st.title("Metodologi")

st.subheader("Metode analisis yang tersedia")
st.markdown(
    """
- **Ringkasan dan demografi:** statistik deskriptif dan visualisasi distribusi data.
- **Faktor risiko:** odds ratio mentah beserta interval kepercayaan 95% untuk
  faktor yang tersedia. Hasil ini belum disesuaikan terhadap faktor perancu.
- **Korelasi:** korelasi peringkat Spearman antara variabel numerik dan skor KPSP.
- **Kualitas data:** pemeriksaan kelengkapan dan beberapa aturan konsistensi data.
- **Pengelolaan data:** tambah, lihat, ubah, hapus, impor, dan ekspor data skrining.
"""
)

st.subheader("Definisi dan batasan")
st.write(
    "Kategori hasil KPSP dan variabel turunan dihitung berdasarkan aturan pada "
    "aplikasi. Buka bagian Definisi & cut-off di halaman analisis untuk melihat "
    "rincian aturan yang digunakan."
)
st.warning(
    "Data bersifat cross-sectional. Hubungan yang terlihat adalah asosiasi, bukan "
    "bukti sebab-akibat. Odds ratio dan korelasi tidak boleh ditafsirkan sebagai "
    "prediksi individual."
)
