import pandas as pd
import streamlit as st

import database as db
import utils as u
from schema import FIELDS, NAMES

u.setup("Kelola Data (CRUD)")
df = db.read_all()


def kosong(v):
    return v is None or (not isinstance(v, str) and pd.isna(v))


def widget(f, val, k, locked=False):
    key, label = f"{k}_{f.name}", f.label + (" *" if f.req else "")
    val = None if kosong(val) else val
    if f.kind == "text":
        return (st.text_input(label, value=val or "", key=key, disabled=locked).strip() or None)
    if f.kind == "date":
        d = pd.Timestamp(val).date() if val is not None else pd.Timestamp.today().date()
        return st.date_input(label, value=d, key=key)
    if f.kind == "int":
        return st.number_input(label, min_value=int(f.lo), max_value=int(f.hi),
                               value=None if val is None else int(val), step=1, key=key)
    if f.kind == "float":
        return st.number_input(label, min_value=float(f.lo), max_value=float(f.hi),
                               value=None if val is None else float(val), step=0.1, format="%.1f", key=key)
    idx = f.opts.index(val) if val in f.opts else None
    return st.selectbox(label, f.opts, index=idx, key=key, placeholder="Pilih...")


def form_fields(d, k, edit=False):
    out = {}
    for grp in dict.fromkeys(f.grp for f in FIELDS):
        with st.expander(grp, expanded=grp.startswith(("1", "8"))):
            cols = st.columns(3)
            for i, f in enumerate([x for x in FIELDS if x.grp == grp]):
                with cols[i % 3]:
                    out[f.name] = widget(f, d.get(f.name), k, locked=(edit and f.name == "id_anak"))
    return out


def wajib_ok(data):
    miss = [f.label for f in FIELDS if f.req and kosong(data[f.name])]
    if miss:
        st.error("Kolom wajib belum diisi: " + ", ".join(miss))
    return not miss


def aksi(fn, *args, pesan):
    try:
        fn(*args)
    except Exception as e:
        st.error(f"Gagal: {str(e)[:300]}")
        return
    st.toast(pesan)
    st.rerun()


mode = st.radio("Aksi", ["Lihat", "Tambah", "Edit", "Hapus", "Impor / Ekspor"], horizontal=True)

if mode == "Lihat":
    st.dataframe(df, hide_index=True)
    st.caption(f"{len(df)} data. Kolom turunan (kategori KPSP dst.) dihitung otomatis oleh database.")

elif mode == "Tambah":
    with st.form("form_tambah"):
        data = form_fields({}, "add")
        if st.form_submit_button("Simpan", type="primary") and wajib_ok(data):
            aksi(db.create, data, pesan="Data ditambahkan")

elif mode == "Impor / Ekspor":
    a, b, c = st.columns(3)
    a.download_button("Unduh template CSV", pd.DataFrame(columns=NAMES).to_csv(index=False).encode(),
                      "template_skrining.csv", "text/csv")
    if len(df):
        b.download_button("Ekspor semua (termasuk turunan)", df.to_csv(index=False).encode(),
                          "skrining_lengkap.csv", "text/csv")
    if c.button("Isi 150 data contoh"):
        db.seed_sample(150)
        st.rerun()
    up = st.file_uploader("Impor CSV (kolom sesuai template)", type="csv")
    if up is not None:
        new = pd.read_csv(up)
        st.dataframe(new.head(10), hide_index=True)
        if st.button("Validasi & impor", type="primary"):
            n, errs = db.import_df(new)
            if errs:
                for e in errs:
                    st.error(e)
            else:
                st.success(f"{n} baris berhasil diimpor")

elif df.empty:
    st.info("Belum ada data.")

elif mode == "Edit":
    sel = st.selectbox("Pilih ID anak", df["id_anak"])
    row = df[df["id_anak"] == sel].iloc[0].to_dict()
    with st.form(f"form_edit_{sel}"):
        data = form_fields(row, f"edit_{sel}", edit=True)
        if st.form_submit_button("Update", type="primary") and wajib_ok({**data, "id_anak": sel}):
            data.pop("id_anak")
            aksi(db.update, sel, data, pesan="Data diperbarui")

else:  # Hapus
    sel = st.selectbox("Pilih ID anak", df["id_anak"])
    st.dataframe(df[df["id_anak"] == sel], hide_index=True)
    ok = st.checkbox("Saya yakin ingin menghapus data ini (tidak bisa dibatalkan)")
    if st.button("Hapus", type="primary", disabled=not ok):
        aksi(db.delete, sel, pesan="Data dihapus")
