import os
import re
import uuid
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from schema import FIELDS, NAMES, BY_NAME, FREQ, FREQ_COLS, GADGET_COND, PEND, YN

load_dotenv()
TABLE = "skrining_dd"
_engine = None


def get_engine():
    global _engine
    if _engine is None:
        url = "postgresql+psycopg2://{u}:{p}@{h}:{port}/{d}".format(
            u=os.getenv("DB_USER", "postgres"), p=quote_plus(os.getenv("DB_PASSWORD", "")),
            h=os.getenv("DB_HOST", "localhost"), port=os.getenv("DB_PORT", "5432"),
            d=os.getenv("DB_NAME", "dashboard_dd"))
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine


# ---------------- DDL ----------------
SQLTYPE = {"text": "VARCHAR(100)", "date": "DATE", "int": "INT", "float": "NUMERIC(6,1)", "cat": "VARCHAR(40)"}


def _lit(opts):
    return ", ".join("'" + o.replace("'", "''") + "'" for o in opts)


def _col_ddl(f):
    s = f"{f.name} {SQLTYPE[f.kind]}"
    if f.name == "id_anak":
        s += " PRIMARY KEY"
    elif f.req:
        s += " NOT NULL"
    if f.kind in ("int", "float") and f.lo is not None:
        s += f" CHECK ({f.name} BETWEEN {f.lo} AND {f.hi})"
    if f.kind == "cat":
        s += f" CHECK ({f.name} IN ({_lit(f.opts)}))"
    return s


def _freq_score(c):
    return f"CASE {c} WHEN 'Sering' THEN 3 WHEN 'Kadang' THEN 2 WHEN 'Jarang' THEN 1 WHEN 'Tidak pernah' THEN 0 END"


def _view_sql():
    # KPSP tersedia untuk usia 3,6,9,12,15,18,21,24,30,36,...,72 bulan; pakai form usia di bawahnya
    ages = [72, 66, 60, 54, 48, 42, 36, 30, 24, 21, 18, 15, 12, 9, 6, 3]
    form = "CASE " + " ".join(f"WHEN usia_koreksi_bulan >= {a} THEN 'KPSP {a} bln'" for a in ages) \
           + " ELSE 'Di bawah 3 bln' END"
    parts = []
    for f in FIELDS:
        cond = f"{f.name} IS NOT NULL"
        if f.name in GADGET_COND:
            cond = f"({cond} OR durasi_gadget_menit = 0)"
        parts.append(f"CASE WHEN {cond} THEN 1 ELSE 0 END")
    lengkap = f"ROUND(100.0 * ({' + '.join(parts)}) / {len(FIELDS)}, 1)"
    freq_sum = " + ".join(f"({_freq_score(c)})" for c in FREQ_COLS)
    inter = ("CASE WHEN durasi_interaksi_menit IS NULL THEN NULL WHEN durasi_interaksi_menit < 30 THEN 0 "
             "WHEN durasi_interaksi_menit < 60 THEN 1 WHEN durasi_interaksi_menit < 120 THEN 2 ELSE 3 END")
    return f"""
CREATE VIEW v_analisis AS
WITH k AS (
  SELECT t.*,
    CASE WHEN usia_kehamilan_minggu < 37 AND usia_anak_bulan <= 24
         THEN GREATEST(usia_anak_bulan - CAST(ROUND((40 - usia_kehamilan_minggu) / 4.345) AS INT), 0)
         ELSE usia_anak_bulan END AS usia_koreksi_bulan,
    CASE WHEN usia_anak_bulan < 12 THEN 12 WHEN usia_anak_bulan < 36 THEN 11
         WHEN usia_anak_bulan <= 60 THEN 10 ELSE 9 END AS tidur_min,
    CASE WHEN usia_anak_bulan < 12 THEN 16 WHEN usia_anak_bulan < 36 THEN 14
         WHEN usia_anak_bulan <= 60 THEN 13 ELSE 12 END AS tidur_maks
  FROM {TABLE} t
), s AS (
  SELECT k.*, {form} AS form_kpsp,
    ({freq_sum}) + ({inter}) AS skor_stimulasi
  FROM k
)
SELECT s.*,
  CASE WHEN skor_kpsp >= 9 THEN 'Sesuai' WHEN skor_kpsp >= 7 THEN 'Meragukan'
       ELSE 'Kemungkinan Penyimpangan' END AS kategori_kpsp,
  CASE WHEN skor_kpsp >= 9 THEN 'Sesuai' ELSE 'Berisiko' END AS kpsp_biner,
  CASE WHEN skor_kpsp >= 9 THEN 'Lanjutkan stimulasi, skrining ulang sesuai jadwal'
       WHEN skor_kpsp >= 7 THEN 'Stimulasi intensif, skrining ulang 2 minggu'
       ELSE 'Rujuk ke fasilitas kesehatan' END AS tindak_lanjut_kpsp,
  CASE WHEN usia_anak_bulan < 12 THEN '0-11 bln' WHEN usia_anak_bulan < 24 THEN '12-23 bln'
       WHEN usia_anak_bulan < 36 THEN '24-35 bln' WHEN usia_anak_bulan < 48 THEN '36-47 bln'
       WHEN usia_anak_bulan <= 60 THEN '48-60 bln' ELSE '61-72 bln' END AS kelompok_usia,
  CASE WHEN berat_lahir_gram < 2500 THEN 'BBLR' ELSE 'Normal' END AS kategori_bblr,
  CASE WHEN usia_kehamilan_minggu < 37 THEN 'Prematur' ELSE 'Cukup bulan' END AS status_prematur,
  CASE WHEN durasi_gadget_menit IS NULL THEN NULL
       WHEN durasi_gadget_menit = 0 THEN 'Tanpa layar'
       WHEN usia_anak_bulan < 24 THEN 'Melebihi batas'
       WHEN durasi_gadget_menit <= 60 THEN 'Dalam batas'
       ELSE 'Melebihi batas' END AS kelompok_durasi_gadget,
  CASE WHEN durasi_tidur_jam IS NULL THEN NULL WHEN durasi_tidur_jam < tidur_min THEN 'Kurang'
       WHEN durasi_tidur_jam > tidur_maks THEN 'Berlebih' ELSE 'Cukup' END AS kategori_tidur,
  CASE WHEN skor_stimulasi IS NULL THEN NULL WHEN skor_stimulasi <= 6 THEN 'Rendah'
       WHEN skor_stimulasi <= 10 THEN 'Sedang' ELSE 'Tinggi' END AS kategori_stimulasi,
  {lengkap} AS kelengkapan_data
FROM s
"""


def init_db():
    with get_engine().begin() as c:
        c.execute(text(f"CREATE TABLE IF NOT EXISTS {TABLE} (\n  "
                       + ",\n  ".join(_col_ddl(f) for f in FIELDS)
                       + ",\n  created_at TIMESTAMP DEFAULT NOW(),\n  updated_at TIMESTAMP DEFAULT NOW())"))
        for f in FIELDS:  # migrasi aditif bila kolom baru ditambahkan di schema.py
            c.execute(text(f"ALTER TABLE {TABLE} ADD COLUMN IF NOT EXISTS {f.name} {SQLTYPE[f.kind]}"))
        c.execute(text("DROP VIEW IF EXISTS v_analisis"))
        c.execute(text(_view_sql()))


# ---------------- CRUD ----------------
NUMERIC = [f.name for f in FIELDS if f.kind in ("int", "float")] + [
    "usia_koreksi_bulan", "tidur_min", "tidur_maks", "skor_stimulasi", "kelengkapan_data"]


def read_all() -> pd.DataFrame:
    df = pd.read_sql(text("SELECT * FROM v_analisis ORDER BY tanggal_skrining DESC, id_anak"), get_engine())
    df["tanggal_skrining"] = pd.to_datetime(df["tanggal_skrining"])
    for c in NUMERIC:
        df[c] = pd.to_numeric(df[c])
    return df


def create(data: dict):
    cols = ", ".join(NAMES)
    vals = ", ".join(f":{c}" for c in NAMES)
    with get_engine().begin() as c:
        c.execute(text(f"INSERT INTO {TABLE} ({cols}) VALUES ({vals})"), data)


def update(id_anak: str, data: dict):
    cols = [n for n in NAMES if n != "id_anak"]
    sets = ", ".join(f"{n} = :{n}" for n in cols)
    with get_engine().begin() as c:
        c.execute(text(f"UPDATE {TABLE} SET {sets}, updated_at = NOW() WHERE id_anak = :id_anak"),
                  {**data, "id_anak": id_anak})


def delete(id_anak: str):
    with get_engine().begin() as c:
        c.execute(text(f"DELETE FROM {TABLE} WHERE id_anak = :i"), {"i": id_anak})


# ---------------- Impor massal ----------------
def prepare_import_df(df: pd.DataFrame):
    """Normalize CSV headers and fill absent optional input columns."""
    aliases = {}
    for f in FIELDS:
        for name in (f.name, f.label):
            key = re.sub(r"[^a-z0-9]", "", name.lower())
            aliases[key] = f.name

    rename = {}
    recognized = set()
    duplicate_fields = set()
    unknown = []
    for column in df.columns:
        key = re.sub(r"[^a-z0-9]", "", str(column).lstrip("\ufeff").strip().lower())
        field = aliases.get(key)
        if field is None:
            unknown.append(str(column))
            continue
        if field in recognized:
            duplicate_fields.add(field)
        recognized.add(field)
        rename[column] = field

    df = df.rename(columns=rename).copy()
    missing_optional = [f.name for f in FIELDS if not f.req and f.name not in df.columns]
    for name in missing_optional:
        df[name] = pd.NA

    errors = []
    if duplicate_fields:
        errors.append("Kolom CSV duplikat setelah penyesuaian: " + ", ".join(sorted(duplicate_fields)))
    return df, missing_optional, unknown, errors


def validate_df(df: pd.DataFrame):
    """Return (df_bersih, daftar_error)."""
    df, _, _, errs = prepare_import_df(df)
    if errs:
        return df, errs
    miss = [f.name for f in FIELDS if f.req and f.name not in df.columns]
    if miss:
        errs.append(f"Kolom wajib tidak ada: {', '.join(miss)}")
        return df, errs
    df = df.reindex(columns=NAMES).copy()
    df["tanggal_skrining"] = pd.to_datetime(df["tanggal_skrining"], errors="coerce").dt.date
    for f in FIELDS:
        s = df[f.name]
        if f.req and s.isna().any():
            errs.append(f"{f.name}: ada {int(s.isna().sum())} nilai kosong (wajib)")
        if f.kind == "cat":
            bad = s.dropna()[~s.dropna().isin(f.opts)]
            if len(bad):
                errs.append(f"{f.name}: nilai tidak valid {sorted(set(map(str, bad)))[:5]}; pilihan: {f.opts}")
        if f.kind in ("int", "float"):
            num = pd.to_numeric(s, errors="coerce")
            bad = s.notna() & (num.isna() | (num < f.lo) | (num > f.hi))
            if bad.any():
                errs.append(f"{f.name}: {int(bad.sum())} nilai di luar rentang {f.lo}-{f.hi}")
            df[f.name] = num.astype("Int64") if f.kind == "int" else num
    if df["id_anak"].duplicated().any():
        errs.append("id_anak duplikat di dalam file")
    return df, errs


def import_df(df: pd.DataFrame):
    df, errs = validate_df(df)
    if errs:
        return 0, errs
    df = df.astype(object).where(df.notna(), None)
    try:
        with get_engine().begin() as c:
            df.to_sql(TABLE, c, if_exists="append", index=False, method="multi")
    except Exception as e:
        return 0, [f"Gagal menyimpan (kemungkinan id_anak sudah ada): {str(e)[:300]}"]
    return len(df), []


# ---------------- Data contoh ----------------
def seed_sample(n: int = 150):
    rng = np.random.default_rng()
    pick = lambda o, p=None: str(rng.choice(o, p=p))
    rows = []
    for _ in range(n):
        usia = int(rng.integers(3, 73))
        hamil = int(rng.choice([30, 33, 35, 36, 37, 38, 39, 40, 41],
                               p=[.01, .02, .03, .04, .08, .17, .30, .28, .07]))
        bbl = int(np.clip(rng.normal(3100 - (40 - min(hamil, 40)) * 90, 450), 1000, 4500))
        gadget = 0 if (usia < 12 and rng.random() < .8) else int(rng.choice([0, 20, 45, 60, 90, 120, 180, 240]))
        fr = {c: pick(FREQ, [.05, .2, .4, .35]) for c in FREQ_COLS}
        inter = int(rng.integers(10, 240))
        stim = sum(FREQ.index(v) for v in fr.values()) + (0 if inter < 30 else 1 if inter < 60 else 2 if inter < 120 else 3)
        tidur = round(float(np.clip(rng.normal(11.5, 1.6), 6, 16)), 1)
        ibu = pick(PEND, [.15, .25, .40, .20])
        melebihi = (usia < 24 and gadget > 0) or gadget > 60
        risk = (1.2 * melebihi + 1.8 * (bbl < 2500) + 1.2 * (hamil < 37)
                + 0.12 * max(8 - stim, 0) + 0.5 * (tidur < 10.5) + 0.4 * (ibu in PEND[:2]))
        skor = int(np.clip(round(9.6 - risk + rng.normal(0, 0.9)), 0, 10))
        bb = round(float(np.clip(3.3 + 0.45 * min(usia, 12) + 0.12 * max(usia - 12, 0) + rng.normal(0, .8), 2, 30)), 1)
        tb = round(float(np.clip(50 + 2 * min(usia, 12) + 0.5 * max(usia - 12, 0) + rng.normal(0, 2), 40, 130)), 1)
        r = {
            "id_anak": "A" + uuid.uuid4().hex[:7].upper(),
            "tanggal_skrining": (pd.Timestamp.today() - pd.Timedelta(days=int(rng.integers(0, 180)))).date(),
            "usia_anak_bulan": usia, "jenis_kelamin": pick(["Laki-laki", "Perempuan"]),
            "jumlah_saudara": int(rng.integers(0, 5)),
            "wilayah": pick(["Wilayah A", "Wilayah B", "Wilayah C", "Wilayah D", "Wilayah E"]),
            "berat_lahir_gram": bbl, "usia_kehamilan_minggu": hamil,
            "riwayat_penyakit_berulang": pick(YN, [.8, .2]),
            "riwayat_gangguan_pendengaran_penglihatan": pick(YN, [.95, .05]),
            "berat_badan_kg": bb, "tinggi_panjang_badan_cm": tb,
            "status_gizi_bb_u": pick(BY["status_gizi_bb_u"], [.03, .12, .75, .10]),
            "status_gizi_pb_tb_u": pick(BY["status_gizi_pb_tb_u"], [.05, .15, .75, .05]),
            "status_gizi_bb_pb_tb": pick(BY["status_gizi_bb_pb_tb"], [.02, .08, .70, .08, .08, .04]),
            "pendidikan_ibu": ibu, "pekerjaan_ibu": pick(BY["pekerjaan_ibu"], [.5, .15, .15, .12, .08]),
            "pendidikan_ayah": pick(PEND, [.15, .25, .40, .20]),
            "pendapatan_keluarga": pick(BY["pendapatan_keluarga"], [.4, .4, .2]),
            "jumlah_anggota_rumah": int(rng.integers(3, 10)),
            "durasi_interaksi_menit": inter, **fr, "respons_orang_tua": pick(BY["respons_orang_tua"], [.15, .45, .4]),
            "durasi_gadget_menit": gadget,
            "jenis_konten_gadget": None if gadget == 0 else pick(BY["jenis_konten_gadget"]),
            "pendampingan_gadget": None if gadget == 0 else pick(BY["pendampingan_gadget"], [.3, .4, .3]),
            "tujuan_penggunaan_gadget": None if gadget == 0 else pick(BY["tujuan_penggunaan_gadget"]),
            "durasi_tidur_jam": tidur, "frekuensi_bermain_tanpa_layar": pick(FREQ, [.03, .12, .4, .45]),
            "pengasuh_utama": pick(BY["pengasuh_utama"], [.7, .05, .2, .05]),
            "durasi_pengasuhan_jam": round(float(rng.uniform(4, 20)), 1),
            "keikutsertaan_paud": pick(YN, [.6, .4]),
            "frekuensi_posyandu": pick(BY["frekuensi_posyandu"], [.6, .3, .1]),
            "riwayat_konsultasi_perkembangan": pick(YN, [.9, .1]),
            "skor_kpsp": skor, "petugas_skrining": pick(["Petugas A", "Petugas B", "Petugas C"]),
        }
        for f in FIELDS:  # sisipkan ~5% data kosong pada kolom opsional
            if not f.req and r[f.name] is not None and rng.random() < .05:
                r[f.name] = None
        rows.append(r)
    ok, errs = import_df(pd.DataFrame(rows))
    if errs:
        raise RuntimeError("; ".join(errs))
    return ok


BY = {f.name: f.opts for f in FIELDS if f.opts}
