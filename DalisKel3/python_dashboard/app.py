import streamlit as st

st.set_page_config(
    page_title="Dashboard Skrining Perkembangan Anak",
    page_icon=":material/monitor_heart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background-color: #111a2e;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        padding-top: 1rem;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        border-radius: 8px;
        margin: 2px 0;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: #35425f;
        color: #f8fafc;
        font-weight: 600;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
        background-color: #26334d;
        color: #ffffff;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {
        color: #aebbd0;
        font-weight: 700;
    }
    .stApp, .stApp p, .stApp label, .stApp [data-testid="stMarkdownContainer"] {
        font-size: 1.05rem;
        line-height: 1.55;
    }
    .stApp h1 {
        font-size: 2.15rem;
    }
    .stApp h2 {
        font-size: 1.7rem;
    }
    .stApp h3 {
        font-size: 1.35rem;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        font-size: 1rem;
    }
    .stApp button, .stApp input, .stApp [role="listbox"] {
        font-size: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

pages = {
    "Beranda": [
        st.Page("pages/8_Beranda.py", title="Beranda", default=True),
    ],
    "Tentang Penelitian": [
        st.Page("pages/5_Tujuan.py", title="Tujuan"),
        st.Page("pages/6_Metodologi.py", title="Metodologi"),
    ],
    "Analisis": [
        st.Page("pages/9_Analisis_Data.py", title="Analisis Data"),
        st.Page("pages/0_Ringkasan.py", title="Ringkasan"),
        st.Page("pages/1_Faktor_Risiko.py", title="Faktor Risiko"),
        st.Page("pages/2_Demografi.py", title="Demografi"),
        st.Page("pages/7_Prediksi.py", title="Prediksi"),
    ],
    "Data": [
        st.Page("pages/3_Kualitas_Data.py", title="Kualitas Data"),
        st.Page("pages/4_Kelola_Data.py", title="Kelola Data"),
    ],
}

st.navigation(pages).run()
