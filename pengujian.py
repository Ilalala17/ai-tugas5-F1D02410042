import json
import subprocess
import sys
from pathlib import Path

import main

ROOT = Path(__file__).resolve().parent
KB = json.loads((ROOT / "knowledge_base.json").read_text(encoding="utf-8"))
PERTANYAAN = main.daftar_pertanyaan(KB)

KASUS = [
    {
        "nama": "Kasus 1 - Kudis",
        "jawaban": [
            "gatal intens",
            "kerontokan",
            "lesi kulit pada telinga, wajah, dan leher",
            "pembentukan kerak pada kulit"
        ],
        "harapan": "kudis"
    },
    {
        "nama": "Kasus 2 - Flu Kucing",
        "jawaban": [
            "kurang nafsu makan",
            "demam",
            "bersin",
            "pilek",
            "sariawan pada lidah dan mulut",
            "lesu"
        ],
        "harapan": "flu kucing"
    },
    {
        "nama": "Kasus 3 - Tidak Terdiagnosis",
        "jawaban": [
            "gatal"
        ],
        "harapan": "tidak ditemukan diagnosis"
    },
    {
        "nama": "Kasus 4 - Cacingan melalui S1",
        "jawaban": [
            "penurunan berat badan",
            "bulu yang kusam",
            "perut buncit",
            "muntah",
            "diare"
        ],
        "harapan": "cacingan"
    },
    {
        "nama": "Kasus 5 - Pijal",
        "jawaban": [
            "iritasi kulit",
            "kerontokan",
            "gatal",
            "anemia"
        ],
        "harapan": "pijal"
    },
    {
        "nama": "Kasus 6 - Infeksi Telinga",
        "jawaban": [
            "pembengkakan pada saluran telinga",
            "keluarnya cairan berwarna gelap dari telinga",
            "kemerahan pada saluran telinga",
            "bau tidak sedap dari telinga",
            "pruritus (gatal di telinga)",
            "menggaruk atau menggosok telinga (trauma)"
        ],
        "harapan": "infeksi telinga"
    },
    {
        "nama": "Kasus 7 - Cacingan melalui S2",
        "jawaban": [
            "kurus (kurang dari berat ideal biasanya)",
            "makan banyak",
            "keluar cacing dari anus",
            "muntah cacing"
        ],
        "harapan": "cacingan"
    },
    {
        "nama": "Kasus 8 - Dua Kesimpulan",
        "jawaban": [
            "iritasi kulit",
            "gatal intens",
            "kerontokan",
            "lesi kulit pada telinga, wajah, dan leher",
            "gatal",
            "pembentukan kerak pada kulit",
            "anemia"
        ],
        "harapan": "kudis, pijal"
    }
]


def jalankan(jawaban_ya):
    jawaban_ya = set(jawaban_ya)
    masukan = "\n".join(
        "y" if gejala["nama"] in jawaban_ya else "t"
        for gejala in PERTANYAAN
    ) + "\n"
    proses = subprocess.run(
        [sys.executable, str(ROOT / "main.py")],
        input=masukan,
        text=True,
        capture_output=True,
        encoding="utf-8"
    )
    return proses.stdout


def ambil_kesimpulan(keluaran):
    for baris in keluaran.splitlines():
        if baris.startswith("Kesimpulan: "):
            return baris[len("Kesimpulan: "):].strip()
    return None


def main_uji():
    lulus = 0
    print("Pengujian sistem pakar penyakit kucing")
    print("=" * 50)
    for kasus in KASUS:
        keluaran = jalankan(kasus["jawaban"])
        kesimpulan = ambil_kesimpulan(keluaran)
        ada_alasan = "Alasan:" in keluaran
        ada_catatan = "Catatan:" in keluaran
        benar = kesimpulan == kasus["harapan"] and ada_alasan and ada_catatan
        status = "LULUS" if benar else "GAGAL"
        print(f"[{status}] {kasus['nama']}")
        print(f"         Harapan : {kasus['harapan']}")
        print(f"         Hasil   : {kesimpulan}")
        if benar:
            lulus += 1
        else:
            print("--------- keluaran program ---------")
            print(keluaran)
            print("------------------------------------")
    print("=" * 50)
    print(f"Hasil: {lulus}/{len(KASUS)} kasus lulus.")
    return 0 if lulus == len(KASUS) else 1


if __name__ == "__main__":
    raise SystemExit(main_uji())
