# Dashboard Developmental Delay pada Anak (Streamlit + PostgreSQL)

## Setup (PowerShell)
1. Buat database kosong:  `CREATE DATABASE dashboard_dd;`
2. Edit `.env` (isi DB_PASSWORD, dll).
3. Jalankan:
```
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```
(Jika Activate.ps1 diblokir: `Set-ExecutionPolicy -Scope Process Bypass`)

Tabel `skrining_dd` dan view `v_analisis` dibuat otomatis. Buka **Kelola Data > Impor/Ekspor > Isi 150 data contoh** untuk mencoba.

## Struktur
- `schema.py`   : definisi 40 kolom input (tipe, wajib/opsional, pilihan, rentang). Ubah di sini untuk menambah/mengubah kolom.
- `database.py` : koneksi, DDL + VIEW turunan, CRUD, impor CSV tervalidasi, data contoh.
- `utils.py`    : setup halaman, filter sidebar, definisi cut-off.
- `app.py`      : Ringkasan. `pages/` : Faktor Risiko, Demografi, Kualitas Data, Kelola Data.

## Kolom turunan (dihitung di VIEW `v_analisis`, tidak diinput)
kategori_kpsp, kpsp_biner, tindak_lanjut_kpsp, usia_koreksi_bulan, form_kpsp, kelompok_usia, kategori_bblr,
status_prematur, kelompok_durasi_gadget, kategori_tidur, skor_stimulasi, kategori_stimulasi, kelengkapan_data.
Aturan kategori ada di `database.py` (`_view_sql`) dan ringkasannya di expander "Definisi" pada dashboard.

## Catatan
- Cut-off (gadget, tidur, skor stimulasi) adalah usulan; sepakati dengan tim lalu ubah di `_view_sql`.
- Menambah kolom baru di `schema.py` otomatis di-ALTER. Mengubah pilihan/rentang kolom lama butuh
  `DROP VIEW v_analisis; DROP TABLE skrining_dd;` (data hilang) atau ubah CHECK manual.
- Tabel lama `anak_skrining` (versi sederhana) tidak dipakai lagi; boleh di-DROP.
- Data anak: gunakan ID pseudonim, jangan simpan nama/NIK/tanggal lahir. Jangan commit `.env`.
- Data cross-sectional: hasil menunjukkan asosiasi, bukan sebab-akibat.
