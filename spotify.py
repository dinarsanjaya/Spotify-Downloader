import os
import re
import logging
import argparse
import requests
import concurrent.futures
from pathlib import Path
import time

# Impor library pihak ketiga
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from yt_dlp import YoutubeDL
from mutagen.mp3 import MP3, EasyMP3
from mutagen.id3 import APIC
from mutagen.flac import Picture, FLAC
from mutagen.mp4 import MP4, MP4Cover
from tqdm import tqdm
from colorama import Fore, Style, init

# Konfigurasi logging dasar untuk output yang bersih
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Memuat variabel lingkungan dari file .env
load_dotenv()
init(autoreset=True)

def sanitize_filename(filename):
    """Menghapus karakter ilegal dari nama file."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def get_spotify_client():
    """Menginisialisasi dan mengembalikan klien Spotipy."""
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    if not client_id or not client_secret:
        logging.error("Kredensial Spotify (SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET) tidak ditemukan.")
        logging.info("Pastikan Anda sudah membuat file .env dan mengisinya.")
        exit()
    try:
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        return spotipy.Spotify(auth_manager=auth_manager)
    except Exception as e:
        logging.error(f"Gagal mengautentikasi dengan Spotify: {e}")
        exit()

def get_track_info(sp, url):
    """Mengambil metadata trek dari URL Spotify (trek, album, atau playlist)."""
    track_list = []
    album_info = None

    try:
        if "track" in url:
            results = sp.track(url)
            track_list.append(results)
        elif "album" in url:
            album_info = sp.album(url)
            results = sp.album_tracks(url)
            for item in results['items']:
                item['album'] = album_info
                track_list.append(item)
        elif "playlist" in url:
            results = sp.playlist_items(url)
            for item in results['items']:
                if item.get('track'):
                    track_list.append(item['track'])
        else:
            logging.warning(f"URL tidak didukung atau tidak valid: {url}")
            return []
    except spotipy.exceptions.SpotifyException as e:
        logging.error(f"Error saat mengambil data dari Spotify: {e}")
        return []

    parsed_tracks = []
    for i, track in enumerate(track_list):
        if not track or not track.get('album'): continue

        album_data = track['album']
        parsed_tracks.append({
            'name': track['name'],
            'artists': [artist['name'] for artist in track['artists']],
            'album': album_data['name'],
            'track_number': track.get('track_number', i+1),
            'total_tracks': album_data.get('total_tracks', len(track_list)),
            'release_date': album_data.get('release_date', ''),
            'album_art_url': album_data['images'][0]['url'] if album_data.get('images') else None,
            'album_artists': [artist['name'] for artist in album_data.get('artists', [])]
        })
    return parsed_tracks

def embed_metadata(audio_file, track_info, audio_format):
    """Menyematkan metadata (termasuk album art) ke file audio."""
    if not track_info.get('album_art_url'):
        image_data = None
    else:
        try:
            response = requests.get(track_info['album_art_url'])
            response.raise_for_status()
            image_data = response.content
        except requests.RequestException as e:
            logging.error(f"Gagal mengunduh album art: {e}")
            image_data = None

    try:
        if audio_format == "mp3":
            audio = MP3(audio_file)
            audio.delete()
            if image_data:
                audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=image_data))
            audio = EasyMP3(audio_file)
            audio['title'] = track_info['name']
            audio['artist'] = ", ".join(track_info['artists'])
            audio['album'] = track_info['album']
            audio['albumartist'] = ", ".join(track_info.get('album_artists', track_info['artists']))
            audio['date'] = track_info['release_date']
            audio['tracknumber'] = f"{track_info['track_number']}/{track_info['total_tracks']}"
            audio.save()
        elif audio_format == "flac":
            audio = FLAC(audio_file)
            audio.delete()
            audio['title'] = track_info['name']
            audio['artist'] = ", ".join(track_info['artists'])
            audio['album'] = track_info['album']
            if image_data:
                pic = Picture(); pic.data = image_data; pic.type = 3; pic.mime = u"image/jpeg"; audio.add_picture(pic)
            audio.save()
        elif audio_format == "m4a":
            audio = MP4(audio_file)
            audio['\xa9nam'] = track_info['name']; audio['\xa9ART'] = ", ".join(track_info['artists']); audio['\xa9alb'] = track_info['album']
            audio['trkn'] = [(track_info['track_number'], track_info['total_tracks'])]
            if image_data:
                audio['covr'] = [MP4Cover(image_data, imageformat=MP4Cover.FORMAT_JPEG)]
            audio.save()
    except Exception as e:
        tqdm.write(f"{Fore.YELLOW}⚠️  Gagal menyematkan metadata untuk {Path(audio_file).name}: {e}")

def download_and_process_track(track_info, output_dir, audio_format):
    """Mengunduh trek dari YouTube, mengonversi, dan menyematkan metadata."""
    artist_name = sanitize_filename(track_info['artists'][0])
    album_name = sanitize_filename(track_info['album'])
    full_track_name = f"{artist_name} - {track_info['name']}"
    sanitized_track_name = sanitize_filename(full_track_name)
    
    final_dir = Path(output_dir) / artist_name / album_name
    final_dir.mkdir(parents=True, exist_ok=True)
    
    final_filepath = final_dir / f"{sanitized_track_name}.{audio_format}"

    if final_filepath.exists():
        return f"{Fore.GREEN}✔️ '{sanitized_track_name}' sudah ada, dilewati."

    search_query = f"{track_info['name']} {track_info['artists'][0]} official audio"
    bytes_downloaded = [0]
    start_time = [time.time()]

    def progress_hook(d):
        if d['status'] == 'downloading':
            bytes_downloaded[0] = d.get('downloaded_bytes', 0)
        elif d['status'] == 'finished':
            bytes_downloaded[0] = d.get('total_bytes', bytes_downloaded[0])

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(final_dir / f"{sanitized_track_name}"),
        'quiet': True,
        'noprogress': True,
        'noplaylist': True,
        'progress_hooks': [progress_hook],
    }
    if audio_format == "flac":
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'flac',
            'preferredquality': '0'  # 0 = lossless
        }]
    else:
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
            'preferredquality': '192'
        }]
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:{search_query}"])
        elapsed = time.time() - start_time[0]
        mbps = (bytes_downloaded[0] * 8 / 1_000_000) / elapsed if elapsed > 0 else 0
        embed_metadata(str(final_filepath), track_info, audio_format)
        return f"{Fore.GREEN}✅ Berhasil mengunduh: {sanitized_track_name} {Fore.CYAN}[{mbps:.2f} Mbps]"
    except Exception as e:
        tqdm.write(f"{Fore.RED}❌ Gagal mengunduh atau memproses '{sanitized_track_name}': {e}")
        return None

def print_banner():
    banner = f"""
{Fore.MAGENTA}{Style.BRIGHT}
╔════════════════════════════════════════════════════════════╗
║                                                          ║
║   {Fore.YELLOW}Spotify Downloader CLI by Dinar Sanjaya{Fore.MAGENTA}         ║
║                                                          ║
╚════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
    print(banner)

def main():
    """Fungsi utama untuk menjalankan program secara interaktif."""
    parser = argparse.ArgumentParser(description="Unduh lagu dari Spotify secara interaktif.")
    parser.add_argument("-o", "--output", default="Musik", help="Direktori output utama (default: Musik).")
    parser.add_argument("-f", "--format", default="mp3", choices=['mp3', 'flac', 'm4a'], help="Format audio output (default: mp3).")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Jumlah unduhan bersamaan (default: 5).")
    args = parser.parse_args()

    sp = get_spotify_client()
    print_banner()
    
    while True:
        url = input(f"{Fore.CYAN}\n>>> Masukkan link Spotify (atau ketik 'exit' untuk keluar): {Style.RESET_ALL}")

        if url.lower() in ['exit', 'quit', 'keluar']:
            print(f"\n{Fore.GREEN}Terima kasih! Program berhenti.{Style.RESET_ALL}")
            break
        
        if not url.strip():
            continue

        tracks = get_track_info(sp, url)
        if not tracks:
            logging.warning(f"{Fore.RED}URL tidak valid atau tidak ada lagu yang ditemukan. Silakan coba lagi.{Style.RESET_ALL}")
            continue

        total_tracks = len(tracks)
        print(f"{Fore.GREEN}✅ Ditemukan {total_tracks} trek.{Style.RESET_ALL}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = [executor.submit(download_and_process_track, track, args.output, args.format) for track in tracks]
            for future in tqdm(concurrent.futures.as_completed(futures), total=total_tracks, desc=f"{Fore.YELLOW}Mengunduh", unit="lagu"):
                try:
                    result = future.result()
                    if result:
                        tqdm.write(result)
                except Exception as exc:
                    tqdm.write(f"{Fore.RED}Sebuah lagu menghasilkan error: {exc}{Style.RESET_ALL}")

        print(f"\n{Fore.GREEN}🎉 Selesai memproses {total_tracks} trek dari link yang diberikan.{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}----------------------------------------------{Style.RESET_ALL}")

if __name__ == "__main__":
    main()