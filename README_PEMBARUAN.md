# V3.3 — Perluasan Sumber Nasional & Daerah Indonesia

## Isi paket
- `app.py`: dashboard dengan pemilih katalog sumber.
- `drought_engine.py`: engine fokus sawah kekeringan, puso, irigasi kering, sedimentasi.
- `sources_indonesia_sawah_irigasi.json`: katalog feed nasional dan query Google News RSS regional.

## Cara pasang
1. Hentikan Streamlit dengan Ctrl+C.
2. Cadangkan `app.py` dan `drought_engine.py`.
3. Ganti kedua file dengan versi dalam paket.
4. Letakkan `sources_indonesia_sawah_irigasi.json` pada folder yang sama dengan `app.py`.
5. Jalankan `python -m streamlit run app.py`.

## Catatan penting
- Katalog mencakup feed nasional dan query Google News RSS untuk berbagai wilayah Indonesia.
- URL bertipe "Kandidat RSS" belum tentu aktif; lakukan uji integrasi di komputer pengguna. Sumber yang gagal muncul di bagian "Sumber gagal diambil".
- Query Google News RSS adalah metode memperluas penelusuran berita terindeks, bukan feed resmi dari media lokal.
- Template YouTube harus diganti dengan channel_id resmi.
- Feed RSS tidak menjamin setiap artikel tentang sawah/irigasi akan terambil; cakupan dipengaruhi indeks sumber, tanggal, kata kunci, dan batas hasil.
- Tidak menambahkan scraping media sosial privat atau bypass login/CAPTCHA.
