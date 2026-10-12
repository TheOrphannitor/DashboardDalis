"""Satu-satunya tempat mendefinisikan kolom input. DDL, form, validasi, dan view diturunkan dari sini."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class F:
    name: str
    kind: str            # text | date | int | float | cat
    label: str
    grp: str
    req: bool = False
    opts: Optional[list] = None
    lo: Optional[float] = None
    hi: Optional[float] = None


YN = ["Tidak", "Ya"]
FREQ = ["Tidak pernah", "Jarang", "Kadang", "Sering"]
PEND = ["SD atau kurang", "SMP", "SMA", "Perguruan tinggi"]

G1, G2, G3, G4, G5, G6, G7, G8 = (
    "1. Identitas anak", "2. Riwayat kelahiran & kesehatan", "3. Pertumbuhan & status gizi",
    "4. Karakteristik keluarga", "5. Stimulasi & interaksi orang tua",
    "6. Gadget & kebiasaan harian", "7. Pengasuhan & layanan kesehatan", "8. Hasil skrining KPSP")

FIELDS = [
    F("id_anak", "text", "ID anak (pseudonim, bukan nama/NIK)", G1, True),
    F("tanggal_skrining", "date", "Tanggal skrining", G1, True),
    F("usia_anak_bulan", "int", "Usia kronologis (bulan)", G1, True, lo=0, hi=72),
    F("jenis_kelamin", "cat", "Jenis kelamin", G1, True, ["Laki-laki", "Perempuan"]),
    F("jumlah_saudara", "int", "Jumlah saudara", G1, lo=0, hi=20),
    F("wilayah", "text", "Wilayah (desa/kelurahan)", G1),

    F("berat_lahir_gram", "int", "Berat lahir (gram)", G2, True, lo=500, hi=6000),
    F("usia_kehamilan_minggu", "int", "Usia kehamilan (minggu)", G2, True, lo=22, hi=44),
    F("riwayat_penyakit_berulang", "cat", "Riwayat penyakit berulang", G2, opts=YN),
    F("riwayat_gangguan_pendengaran_penglihatan", "cat", "Gangguan pendengaran/penglihatan", G2, opts=YN),

    F("berat_badan_kg", "float", "Berat badan (kg)", G3, lo=2, hi=30),
    F("tinggi_panjang_badan_cm", "float", "Tinggi/panjang badan (cm)", G3, lo=40, hi=130),
    F("status_gizi_bb_u", "cat", "Status gizi BB/U", G3,
      opts=["Gizi buruk", "Gizi kurang", "Gizi baik", "Risiko gizi lebih"]),
    F("status_gizi_pb_tb_u", "cat", "Status gizi PB/TB/U", G3,
      opts=["Sangat pendek", "Pendek", "Normal", "Tinggi"]),
    F("status_gizi_bb_pb_tb", "cat", "Status gizi BB/PB-TB", G3,
      opts=["Gizi buruk", "Gizi kurang", "Gizi baik", "Berisiko gizi lebih", "Gizi lebih", "Obesitas"]),

    F("pendidikan_ibu", "cat", "Pendidikan ibu", G4, opts=PEND),
    F("pekerjaan_ibu", "cat", "Pekerjaan ibu", G4,
      opts=["Ibu rumah tangga", "Petani/Buruh", "Wiraswasta", "Pegawai/PNS", "Lainnya"]),
    F("pendidikan_ayah", "cat", "Pendidikan ayah", G4, opts=PEND),
    F("pendapatan_keluarga", "cat", "Pendapatan keluarga (rentang)", G4,
      opts=["< 1x UMK", "1-2x UMK", "> 2x UMK"]),
    F("jumlah_anggota_rumah", "int", "Jumlah anggota rumah", G4, lo=2, hi=20),

    F("durasi_interaksi_menit", "int", "Durasi interaksi (menit/hari)", G5, lo=0, hi=1440),
    F("frekuensi_bermain", "cat", "Frekuensi bermain bersama", G5, opts=FREQ),
    F("frekuensi_membaca", "cat", "Frekuensi membaca bersama", G5, opts=FREQ),
    F("frekuensi_mengajak_bicara", "cat", "Frekuensi mengajak bicara", G5, opts=FREQ),
    F("frekuensi_aktivitas_motorik", "cat", "Frekuensi aktivitas motorik", G5, opts=FREQ),
    F("respons_orang_tua", "cat", "Respons orang tua", G5, opts=["Rendah", "Sedang", "Tinggi"]),

    F("durasi_gadget_menit", "int", "Durasi gadget (menit/hari)", G6, lo=0, hi=1440),
    F("jenis_konten_gadget", "cat", "Jenis konten gadget", G6,
      opts=["Edukasi", "Hiburan/Video", "Game", "Campuran"]),
    F("pendampingan_gadget", "cat", "Pendampingan gadget", G6, opts=["Selalu", "Kadang", "Tidak pernah"]),
    F("tujuan_penggunaan_gadget", "cat", "Tujuan penggunaan gadget", G6,
      opts=["Edukasi", "Hiburan", "Menenangkan anak", "Lainnya"]),
    F("durasi_tidur_jam", "float", "Durasi tidur (jam/hari)", G6, lo=0, hi=24),
    F("frekuensi_bermain_tanpa_layar", "cat", "Frekuensi bermain tanpa layar", G6, opts=FREQ),

    F("pengasuh_utama", "cat", "Pengasuh utama", G7, opts=["Ibu", "Ayah", "Nenek/Kakek", "Pengasuh lain"]),
    F("durasi_pengasuhan_jam", "float", "Durasi pengasuhan (jam/hari)", G7, lo=0, hi=24),
    F("keikutsertaan_paud", "cat", "Ikut PAUD", G7, opts=YN),
    F("frekuensi_posyandu", "cat", "Frekuensi posyandu", G7, opts=["Rutin", "Kadang", "Tidak pernah"]),
    F("riwayat_konsultasi_perkembangan", "cat", "Pernah konsultasi perkembangan", G7, opts=YN),

    F("skor_kpsp", "int", "Skor KPSP (0-10)", G8, True, lo=0, hi=10),
    F("petugas_skrining", "text", "Petugas skrining", G8, True),
]

NAMES = [f.name for f in FIELDS]
BY_NAME = {f.name: f for f in FIELDS}
FREQ_COLS = ["frekuensi_bermain", "frekuensi_membaca", "frekuensi_mengajak_bicara",
             "frekuensi_aktivitas_motorik"]
# Kolom ini tidak wajib diisi bila anak tidak memakai gadget (durasi = 0)
GADGET_COND = ["jenis_konten_gadget", "pendampingan_gadget", "tujuan_penggunaan_gadget"]
