import pandas as pd
import streamlit as st

import database as db
import utils as u
from schema import FIELDS

u.setup("Kualitas Data")
df = db.read_all()

if df.empty:
    st.info("Belum ada data untuk diperiksa. Tambahkan data melalui halaman Kelola Data.")
    st.stop()

st.write("Pilih kolom dan pemeriksaan. Hasil diperbarui otomatis mengikuti pilihan Anda.")
field_by_name = {field.name: field for field in FIELDS}

kolom = st.selectbox(
    "Kolom yang diperiksa",
    list(field_by_name),
    format_func=lambda name: field_by_name[name].label,
)
pemeriksaan = st.multiselect(
    "Pemeriksaan",
    ["Kelengkapan", "Validitas nilai", "Ringkasan nilai"],
    default=["Kelengkapan", "Validitas nilai"],
)

field = field_by_name[kolom]
values = df[kolom]
validity = pd.Series(False, index=df.index)

if field.kind == "cat":
    validity = values.notna() & ~values.isin(field.opts or [])
elif field.kind in ("int", "float"):
    numeric = pd.to_numeric(values, errors="coerce")
    validity = values.notna() & (
        numeric.isna()
        | (numeric < field.lo)
        | (numeric > field.hi)
    )
    if field.kind == "int":
        validity |= values.notna() & numeric.notna() & (numeric % 1 != 0)
elif field.kind == "date":
    parsed = pd.to_datetime(values, errors="coerce")
    validity = values.notna() & parsed.isna()
elif field.kind == "text":
    validity = values.astype("string").str.len().gt(100).fillna(False)

missing = values.isna()
summary = []
if "Kelengkapan" in pemeriksaan:
    summary.append({
        "Pemeriksaan": "Nilai kosong",
        "Jumlah": int(missing.sum()),
        "Persentase": f"{missing.mean() * 100:.1f}%",
        "Hasil": "Perlu ditinjau" if missing.any() else "Lulus",
    })
if "Validitas nilai" in pemeriksaan:
    summary.append({
        "Pemeriksaan": "Nilai tidak valid",
        "Jumlah": int(validity.sum()),
        "Persentase": f"{validity.mean() * 100:.1f}%",
        "Hasil": "Perlu ditinjau" if validity.any() else "Lulus",
    })
if "Ringkasan nilai" in pemeriksaan:
    non_null = values.dropna()
    summary.append({
        "Pemeriksaan": "Nilai unik",
        "Jumlah": int(non_null.nunique()),
        "Persentase": "-",
        "Hasil": f"{len(non_null)} nilai terisi",
    })

st.subheader(f"Hasil pemeriksaan: {field.label}")
if summary:
    st.dataframe(pd.DataFrame(summary), hide_index=True, use_container_width=True)
else:
    st.info("Pilih minimal satu jenis pemeriksaan.")

if "Ringkasan nilai" in pemeriksaan and values.notna().any():
    if field.kind in ("int", "float"):
        numeric = pd.to_numeric(values, errors="coerce").dropna()
        a, b, c = st.columns(3)
        a.metric("Minimum", f"{numeric.min():g}")
        b.metric("Median", f"{numeric.median():g}")
        c.metric("Maksimum", f"{numeric.max():g}")
    else:
        st.write("Nilai paling sering muncul")
        counts = values.fillna("(kosong)").value_counts().head(10).rename_axis("Nilai").reset_index(name="Jumlah")
        st.dataframe(counts, hide_index=True, use_container_width=True)

if "Kelengkapan" in pemeriksaan or "Validitas nilai" in pemeriksaan:
    issue_mask = pd.Series(False, index=df.index)
    if "Kelengkapan" in pemeriksaan:
        issue_mask |= missing
    if "Validitas nilai" in pemeriksaan:
        issue_mask |= validity

    if st.checkbox("Tampilkan baris yang perlu ditinjau"):
        if issue_mask.any():
            id_columns = [name for name in ("id_anak", "tanggal_skrining") if name in df.columns and name != kolom]
            details = df.loc[issue_mask, id_columns].copy()
            details[field.label] = values.loc[issue_mask]
            details["Masalah"] = [
                ", ".join(
                    label for label, mask in (
                        ("kosong", missing if "Kelengkapan" in pemeriksaan else None),
                        ("tidak valid", validity if "Validitas nilai" in pemeriksaan else None),
                    ) if mask is not None and mask.loc[index]
                )
                for index in details.index
            ]
            st.dataframe(details, hide_index=True, use_container_width=True)
        else:
            st.success("Tidak ada baris yang perlu ditinjau untuk pemeriksaan ini.")
