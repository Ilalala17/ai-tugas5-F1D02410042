import json
import sys
from pathlib import Path


def muat_knowledge_base(path):
    with open(path, "r", encoding="utf-8") as file:
        kb = json.load(file)
    if "aturan" not in kb or not isinstance(kb["aturan"], list):
        raise ValueError("knowledge_base.json tidak memiliki daftar 'aturan'.")
    return kb


def daftar_semua_gejala(kb):
    hasil = []
    sudah = set()
    for gejala in kb.get("gejala", []):
        nama = gejala["nama"]
        if nama not in sudah:
            hasil.append(gejala)
            sudah.add(nama)
    for aturan in kb["aturan"]:
        for nama in aturan["jika"]:
            if nama not in sudah:
                hasil.append({
                    "kode": "-",
                    "nama": nama,
                    "tanya": f"Apakah kucing mengalami {nama}?"
                })
                sudah.add(nama)
    return hasil


def daftar_pertanyaan(kb):
    anteseden = {syarat for aturan in kb["aturan"] for syarat in aturan["jika"]}
    kesimpulan = {aturan["maka"] for aturan in kb["aturan"]}
    hasil = []
    for gejala in daftar_semua_gejala(kb):
        if gejala["nama"] in anteseden and gejala["nama"] not in kesimpulan:
            hasil.append(gejala)
    return hasil


def tanya_ya_tidak(teks):
    jawaban_ya = {"y", "ya", "yes"}
    jawaban_tidak = {"t", "tidak", "no", "n"}
    while True:
        try:
            jawaban = input(teks).strip().lower()
        except EOFError:
            print()
            raise SystemExit("Input berakhir sebelum semua pertanyaan dijawab.")
        if jawaban in jawaban_ya:
            return True
        if jawaban in jawaban_tidak:
            return False
        print("Jawab dengan y atau t.")


def kondisi_terpenuhi(aturan, fakta):
    syarat = aturan["jika"]
    mode = aturan.get("mode", "dan").lower()
    if mode == "dan":
        return all(butir in fakta for butir in syarat)
    if mode == "atau":
        return any(butir in fakta for butir in syarat)
    raise ValueError(f"Mode aturan {aturan['id']} tidak dikenal: {mode}")


def inferensi(kb, fakta_awal):
    fakta = set(fakta_awal)
    urutan = list(fakta_awal)
    jejak = {}
    siklus = 0

    while True:
        kandidat = None
        for aturan in kb["aturan"]:
            if aturan["maka"] in fakta:
                continue
            if kondisi_terpenuhi(aturan, fakta):
                kandidat = aturan
                break

        if kandidat is None:
            siklus += 1
            print(f"Siklus {siklus}: tidak ada aturan baru, berhenti")
            break

        siklus += 1
        hasil = kandidat["maka"]
        fakta.add(hasil)
        urutan.append(hasil)
        syarat_terpakai = [butir for butir in kandidat["jika"] if butir in fakta]
        jejak[hasil] = (kandidat, syarat_terpakai)
        print(f"Siklus {siklus}: {kandidat['id']} -> {hasil}")

    return urutan, jejak


def fakta_konklusi(kb, urutan):
    anteseden = {syarat for aturan in kb["aturan"] for syarat in aturan["jika"]}
    kesimpulan = {aturan["maka"] for aturan in kb["aturan"]}
    return [fakta for fakta in urutan if fakta in kesimpulan and fakta not in anteseden]


def cetak_alasan(fakta, jejak, level=1):
    if fakta not in jejak:
        return
    aturan, syarat = jejak[fakta]
    indentasi = "  " * level
    print(f"{indentasi}{fakta}  <- {aturan['id']} ({', '.join(syarat)})")
    for butir in syarat:
        if butir in jejak:
            cetak_alasan(butir, jejak, level + 1)


def main():
    lokasi_kb = Path(__file__).with_name("knowledge_base.json")
    try:
        kb = muat_knowledge_base(lokasi_kb)
    except FileNotFoundError:
        print(f"File aturan tidak ditemukan: {lokasi_kb}")
        return 1
    except (json.JSONDecodeError, ValueError) as error:
        print(f"File aturan bermasalah: {error}")
        return 1

    print(kb.get("judul", "Sistem Pakar"))
    print("Jawab y/t.")
    pertanyaan = daftar_pertanyaan(kb)
    fakta_awal = []
    for nomor, gejala in enumerate(pertanyaan, 1):
        teks = gejala.get("tanya") or f"Apakah kucing mengalami {gejala['nama']}?"
        if tanya_ya_tidak(f"{nomor}. {teks} (y/t) > "):
            fakta_awal.append(gejala["nama"])

    print()
    if fakta_awal:
        print("Fakta awal: " + ", ".join(fakta_awal))
    else:
        print("Fakta awal: tidak ada")
    print()

    urutan, jejak = inferensi(kb, fakta_awal)
    konklusi = fakta_konklusi(kb, urutan)

    print()
    if konklusi:
        print("Kesimpulan: " + ", ".join(konklusi))
        print("Alasan:")
        for fakta in konklusi:
            cetak_alasan(fakta, jejak)
    else:
        print("Kesimpulan: tidak ditemukan diagnosis")
        print("Alasan:")
        print("    Tidak ada aturan yang seluruh kondisinya terpenuhi.")

    print()
    print(f"Catatan: {kb.get('batas', '-')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
