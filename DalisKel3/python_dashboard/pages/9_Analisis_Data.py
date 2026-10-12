import pandas as pd
import plotly.express as px
import streamlit as st

from chart_builder import drag_drop
import utils as u
from schema import FIELDS

u.setup("Analisis Data")
df = u.load()

st.write(
    "Saring data, lalu susun visualisasi sendiri dengan menarik kolom ke area "
    "Sumbu X, Sumbu Y, dan Warna."
)

with st.container(border=True):
    st.subheader("Filter data")
    dates = df["tanggal_skrining"].dropna()
    if dates.empty:
        st.warning("Tidak ada tanggal skrining untuk digunakan sebagai filter.")
        filtered = df.copy()
    else:
        date_min, date_max = dates.min().date(), dates.max().date()
        date_range = st.date_input(
            "Periode skrining",
            value=(date_min, date_max),
            min_value=date_min,
            max_value=date_max,
            key="analysis_builder_date_range",
        )
        first_row, second_row = st.columns(2)
        with first_row:
            age_options = [age for age in u.URUT_USIA if age in set(df["kelompok_usia"].dropna())]
            ages = st.multiselect(
                "Kelompok usia",
                age_options,
                key="analysis_builder_ages",
                placeholder="Semua kelompok usia",
            )
            sexes = st.multiselect(
                "Jenis kelamin",
                sorted(df["jenis_kelamin"].dropna().unique()),
                key="analysis_builder_sexes",
                placeholder="Semua jenis kelamin",
            )
        with second_row:
            staff = st.multiselect(
                "Petugas skrining",
                sorted(df["petugas_skrining"].dropna().unique()),
                key="analysis_builder_staff",
                placeholder="Semua petugas",
            )
            outcomes = st.multiselect(
                "Hasil KPSP",
                [outcome for outcome in u.URUT if outcome in set(df["kategori_kpsp"].dropna())],
                key="analysis_builder_outcomes",
                placeholder="Semua hasil",
            )

        filtered = df.copy()
        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
            filtered = filtered[
                filtered["tanggal_skrining"].dt.date.between(date_range[0], date_range[1])
            ]
        if ages:
            filtered = filtered[filtered["kelompok_usia"].isin(ages)]
        if sexes:
            filtered = filtered[filtered["jenis_kelamin"].isin(sexes)]
        if staff:
            filtered = filtered[filtered["petugas_skrining"].isin(staff)]
        if outcomes:
            filtered = filtered[filtered["kategori_kpsp"].isin(outcomes)]

    st.caption(f"{len(filtered):,} dari {len(df):,} baris sesuai filter")

if filtered.empty:
    st.warning("Tidak ada baris yang sesuai dengan pilihan filter.")
    st.stop()

field_labels = {field.name: field.label for field in FIELDS}
field_labels.update({
    "kategori_kpsp": "Kategori KPSP",
    "kpsp_biner": "Status risiko KPSP",
    "tindak_lanjut_kpsp": "Tindak lanjut KPSP",
    "usia_koreksi_bulan": "Usia koreksi (bulan)",
    "form_kpsp": "Form KPSP",
    "kelompok_usia": "Kelompok usia",
    "kategori_bblr": "Kategori BBLR",
    "status_prematur": "Status prematur",
    "kelompok_durasi_gadget": "Kelompok durasi gadget",
    "kategori_tidur": "Kategori tidur",
    "skor_stimulasi": "Skor stimulasi",
    "kategori_stimulasi": "Kategori stimulasi",
    "kelengkapan_data": "Kelengkapan data (%)",
})
excluded = {"created_at", "updated_at"}
field_names = [column for column in filtered.columns if column not in excluded]
display_to_column = {
    f"{field_labels.get(column, column)} · {column}": column
    for column in field_names
}
display_fields = list(display_to_column)

st.subheader("Susun visualisasi")
st.caption("Tarik kolom dari Daftar Kolom ke area sumbu. Tarik kembali ke Daftar Kolom untuk melepasnya.")

if "analysis_builder_version" not in st.session_state:
    st.session_state.analysis_builder_version = 0
if st.button("Kosongkan kanvas", key="analysis_builder_clear"):
    st.session_state.analysis_builder_version += 1
    st.rerun()

sortable_layout = [
    {"header": "Daftar Kolom", "items": display_fields.copy()},
    {"header": "Sumbu X", "items": []},
    {"header": "Sumbu Y", "items": []},
    {"header": "Warna (opsional)", "items": []},
]
layout = drag_drop(
    sortable_layout,
    reset_key=st.session_state.analysis_builder_version,
    key="analysis_builder_sort",
)

areas = {
    section["header"]: [display_to_column[item] for item in section["items"] if item in display_to_column]
    for section in layout
}
x_fields = areas.get("Sumbu X", [])
y_fields = areas.get("Sumbu Y", [])
color_fields = areas.get("Warna (opsional)", [])
if len(x_fields) > 1 or len(y_fields) > 1 or len(color_fields) > 1:
    st.warning("Gunakan satu kolom per area sumbu dan warna. Kolom tambahan belum digunakan pada grafik.")

x = x_fields[0] if x_fields else None
y = y_fields[0] if y_fields else None
color = color_fields[0] if color_fields else None

control_left, control_right = st.columns(2)
with control_left:
    chart_type = st.selectbox(
        "Jenis grafik",
        ["Batang", "Garis", "Sebar", "Histogram", "Lingkaran", "Box plot"],
        key="analysis_builder_chart_type",
    )
with control_right:
    aggregation = st.selectbox(
        "Agregasi untuk grafik batang/garis",
        ["Jumlah baris", "Jumlah nilai", "Total", "Rata-rata", "Median"],
        key="analysis_builder_aggregation",
        help="Agregasi hanya digunakan untuk grafik batang dan garis.",
    )

st.subheader("Visualisasi")
if not x:
    st.info("Tarik satu kolom ke area Sumbu X untuk mulai membuat grafik.")
elif chart_type in ("Sebar", "Box plot") and not y:
    st.info("Tarik satu kolom ke area Sumbu Y untuk jenis grafik ini.")
elif chart_type in ("Sebar", "Box plot") and not pd.api.types.is_numeric_dtype(filtered[y]):
    st.warning("Sumbu Y untuk grafik ini harus berupa kolom numerik.")
elif chart_type == "Sebar" and not pd.api.types.is_numeric_dtype(filtered[x]):
    st.warning("Sumbu X untuk grafik sebar harus berupa kolom numerik.")
else:
    plot_data = filtered.copy()
    if chart_type in ("Batang", "Garis"):
        group_columns = [column for column in (x, color) if column]
        if aggregation == "Jumlah baris":
            plot_data = plot_data.groupby(group_columns, dropna=False).size().reset_index(name="Jumlah baris")
            metric = "Jumlah baris"
        else:
            if not y:
                st.warning("Pilih kolom Sumbu Y untuk agregasi selain Jumlah baris.")
                st.stop()
            if not pd.api.types.is_numeric_dtype(plot_data[y]):
                st.warning("Sumbu Y untuk agregasi harus berupa kolom numerik.")
                st.stop()
            if aggregation == "Jumlah nilai":
                metric = f"Jumlah {y}"
                plot_data = plot_data.groupby(group_columns, dropna=False)[y].count().reset_index(name=metric)
            else:
                function = {"Total": "sum", "Rata-rata": "mean", "Median": "median"}[aggregation]
                metric = f"{aggregation} {y}"
                plot_data = plot_data.groupby(group_columns, dropna=False)[y].agg(function).reset_index(name=metric)

        figure = (
            px.bar(plot_data, x=x, y=metric, color=color, title=f"{aggregation} berdasarkan {field_labels.get(x, x)}")
            if chart_type == "Batang"
            else px.line(plot_data, x=x, y=metric, color=color, markers=True,
                         title=f"{aggregation} berdasarkan {field_labels.get(x, x)}")
        )
        st.plotly_chart(figure, use_container_width=True)
    elif chart_type == "Sebar":
        st.plotly_chart(px.scatter(plot_data, x=x, y=y, color=color), use_container_width=True)
    elif chart_type == "Histogram":
        st.plotly_chart(px.histogram(plot_data, x=x, color=color), use_container_width=True)
    elif chart_type == "Lingkaran":
        st.plotly_chart(px.pie(plot_data, names=x, color=color), use_container_width=True)
    else:
        st.plotly_chart(px.box(plot_data, x=x, y=y, color=color), use_container_width=True)
