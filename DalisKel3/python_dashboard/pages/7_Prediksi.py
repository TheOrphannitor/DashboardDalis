import streamlit as st

st.title("Prediksi")

st.subheader("Prediksi individual belum tersedia")
st.write(
    "Aplikasi ini belum memiliki model prediksi yang dilatih dan divalidasi. "
    "Karena itu, dashboard tidak menghasilkan estimasi risiko individual."
)
st.info(
    "Halaman Faktor Risiko menampilkan odds ratio mentah untuk eksplorasi asosiasi. "
    "Angka tersebut bukan probabilitas prediksi dan tidak digunakan untuk "
    "menggantikan penilaian tenaga kesehatan."
)
