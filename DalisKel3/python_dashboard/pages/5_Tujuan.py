import streamlit as st

st.title("Tujuan Penelitian")

st.subheader("Tujuan")
st.write(
    "Dashboard ini membantu menyajikan dan mengeksplorasi data skrining perkembangan "
    "anak menggunakan hasil KPSP."
)

st.markdown(
    """
- Merangkum hasil skrining dan tindak lanjut yang tercatat.
- Menggambarkan karakteristik anak dan keluarga.
- Mengeksplorasi keterkaitan faktor yang tercatat dengan kategori hasil KPSP.
- Memantau kelengkapan data dan mengelola data skrining.
"""
)
st.info(
    "Hasil analisis pada dashboard ini digunakan untuk eksplorasi data, bukan untuk "
    "menetapkan diagnosis atau memprediksi kondisi seorang anak."
)
