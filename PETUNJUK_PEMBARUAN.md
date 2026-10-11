# Pembaruan Drought Early Warning V3.1 — dukungan feed bernama

## Yang berubah
- Kolom sumber tambahan menerima satu sumber per baris.
- Format yang didukung: `Nama Sumber | URL RSS` atau URL RSS saja.
- Tipe sumber diberi label berdasarkan feed/URL (Google News, YouTube, Instagram, Facebook, X, atau feed publik).
- Aplikasi memberi penjelasan bahwa URL profil Instagram biasa bukan RSS.
- Mesin pencarian tetap memakai RSS/Atom dan Google News; pembaruan ini TIDAK membuat scraper Instagram atau konektor Meta API.

## Cara memasang
1. Hentikan Streamlit di terminal dengan `Ctrl+C`.
2. Buat salinan cadangan `app.py` dan `drought_engine.py` yang sekarang.
3. Salin kedua file dari paket ini ke folder project, timpa file lama.
4. Aktifkan virtual environment jika belum aktif.
5. Jalankan `python -m streamlit run app.py`.

## Format sumber tambahan
Satu sumber per baris, misalnya:
`Nama Sumber | https://alamat-feed-yang-valid/rss`

Untuk YouTube, RSS kanal biasanya berbentuk:
`YouTube Nama Kanal | https://www.youtube.com/feeds/videos.xml?channel_id=UC...`
Ganti `UC...` dengan channel ID kanal publik yang benar.

Untuk Instagram, jangan memasukkan URL profil biasa dan menganggapnya sebagai feed. Diperlukan hasil yang memang tersedia dari pengindeksan publik atau integrasi API resmi Meta yang memenuhi syarat akses. Paket ini belum mengambil posting Instagram secara langsung.

## Catatan
Pastikan feed bisa diakses dari komputer dan mengembalikan RSS/Atom yang valid. Tidak semua situs menyediakan RSS. Uji dengan satu feed terlebih dahulu sebelum menambahkan banyak sumber.
