# Spotify Downloader CLI

## 🇮🇩 Bahasa Indonesia

**Spotify Downloader CLI** adalah aplikasi terminal untuk mengunduh lagu, album, atau playlist dari Spotify dengan metadata lengkap dan cover album. Audio diambil dari YouTube dan dikonversi ke format MP3, FLAC, atau M4A sesuai pilihan. Metadata dan cover album diambil langsung dari Spotify.

### Fitur

- Download lagu, album, atau playlist Spotify.
- Mendukung format audio: `mp3`, `flac`, `m4a`.
- Metadata lengkap: judul, artis, album, nomor track, tanggal rilis, cover album.
- Tampilan CLI interaktif dan berwarna.
- Multi-thread download untuk kecepatan maksimal.

### Instalasi

1. **Clone Repository**
    ```sh
    git clone https://github.com/dinarsanjaya/Spotify-Downloader
    cd Spotify-Downloader
    ```
2. **Install Dependencies**
    ```sh
    pip install -r requirements.txt
    ```
3. **Install FFmpeg (Wajib)**
    ```sh
    winget install ffmpeg
    ```
    Pastikan FFmpeg sudah ada di PATH.

4. **Buat file `.env`**
    ```
    SPOTIPY_CLIENT_ID=isi_client_id_spotify
    SPOTIPY_CLIENT_SECRET=isi_client_secret_spotify
    ```
    Cara mendapatkan Client ID dan Secret:
    - Daftar di [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
    - Buat aplikasi baru, lalu copy Client ID dan Client Secret.

### Cara Pakai

Jalankan program di terminal:
```sh
python spotify.py
```
Ikuti instruksi di layar, masukkan link Spotify (track, album, atau playlist).

Contoh:
```
>>> Masukkan link Spotify (atau ketik 'exit' untuk keluar): https://open.spotify.com/album/xxxxxxx
```

Pilih format audio dan folder output jika ingin custom:
```sh
python spotify.py -f flac -o MusikSaya
```

### Catatan

- Audio diambil dari YouTube, bukan langsung dari Spotify.
- Format FLAC tetap tergantung kualitas sumber YouTube (bukan lossless asli Spotify).
- Metadata dan cover album diambil dari Spotify.

### Kontributor

- Dinar Sanjaya
- GitHub Copilot

---

## 🇬🇧 English

**Spotify Downloader CLI** is a terminal application to download songs, albums, or playlists from Spotify with complete metadata and album cover. Audio is sourced from YouTube and converted to MP3, FLAC, or M4A as you choose. Metadata and album cover are fetched directly from Spotify.

### Features

- Download Spotify tracks, albums, or playlists.
- Supports audio formats: `mp3`, `flac`, `m4a`.
- Complete metadata: title, artist, album, track number, release date, album cover.
- Interactive and colorful CLI display.
- Multi-threaded download for maximum speed.

### Installation

1. **Clone Repository**
    ```sh
    git clone https://github.com/dinarsanjaya/Spotify-Downloader
    cd Spotify-Downloader
    ```
2. **Install Dependencies**
    ```sh
    pip install -r requirements.txt
    ```
3. **Install FFmpeg (Required)**
    ```sh
    winget install ffmpeg
    ```
    Make sure FFmpeg is in your PATH.

4. **Create `.env` file**
    ```
    SPOTIPY_CLIENT_ID=your_spotify_client_id
    SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
    ```
    How to get Client ID and Secret:
    - Register at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
    - Create a new app, then copy the Client ID and Client Secret.

### Usage

Run the program in terminal:
```sh
python spotify.py
```
Follow the instructions, enter a Spotify link (track, album, or playlist).

Example:
```
>>> Enter Spotify link (or type 'exit' to quit): https://open.spotify.com/album/xxxxxxx
```

Choose audio format and output folder if you want custom:
```sh
python spotify.py -f flac -o MyMusic
```

### Notes

- Audio is sourced from YouTube, not directly from Spotify.
- FLAC format depends on YouTube source quality (not original Spotify lossless).
- Metadata and album cover are fetched from Spotify.

### Contributors

- Dinar Sanjaya
