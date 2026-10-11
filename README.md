# Drought Early Warning & News Intelligence V3

## Tujuan

Memantau indikasi kekeringan berdasarkan berita dan sumber konten publik/terindeks.

## Fitur

- Tema dan keyword kekeringan.
- Google News RSS.
- RSS publik tambahan.
- Relevansi 0-100.
- Skor risiko kekeringan 0-100.
- Kategori risiko rendah/sedang/tinggi.
- Deteksi indikator: defisit air, air bersih, pertanian, irigasi, waduk/embung, darurat.
- Deteksi wilayah berbasis kamus.
- Tren harian.
- Dashboard early warning.
- Histori SQLite.
- Export Excel.
- Unit test.

## Media sosial

V3 menyediakan kolom `Tipe Sumber` dan dapat menerima sumber publik melalui RSS/API resmi atau konten sosial yang diindeks oleh mesin pencari. V3 tidak melakukan bypass login, CAPTCHA, private account, atau mengambil data nonpublik.

Untuk koneksi platform tertentu, gunakan API resmi/connector yang memiliki izin.

## Instalasi Windows

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

Buka:

http://localhost:8501

## Interpretasi

Skor risiko adalah indikator berbasis teks, bukan indeks kekeringan hidrologis resmi. Untuk keputusan teknis, kombinasikan dengan curah hujan, SPI/SPEI, debit, elevasi muka air waduk, luas baku sawah, dan data lapangan.

## Roadmap V4

- API media sosial resmi.
- YouTube/social public monitoring.
- semantic similarity.
- anomaly detection.
- peta GIS.
- integrasi BMKG/instansi data resmi.
- laporan PDF harian.
- email/Telegram alert.
- dashboard multi-user.
