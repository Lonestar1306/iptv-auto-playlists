import urllib.parse
import os
import sys
import re

try:
    import requests
except ImportError:
    print("[!] Errore: la libreria 'requests' non è installata.")
    print("[!] Installala eseguendo: pip install requests")
    sys.exit(1)

# ============================================= #
# CONFIGURAZIONE GENERALE EASYPROXY E DIRECTORY #
# ============================================= #
EASYPROXY_BASE_URL = ""
OUTPUT_DIR = "/output"

# ========================================== #
# PARAMETRI DADDYLIVE                        #
# ========================================== #
DADDY_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "daddylive.m3u")
DADDY_DOMAIN = "https://dlive.sx"
DADDY_CHANNELS_URL = f"{DADDY_DOMAIN}/24-7-channels.php"

# ========================================== #
# PARAMETRI LIVETV (GitHub)                  #
# ========================================== #
LIVETV_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "livetv_master.m3u")
LIVETV_EPG_FILE = os.path.join(OUTPUT_DIR, "livetv_epg.xml.gz")

# URL di base per i raw della repository LIVETV
LIVETV_RAW_BASE_URL = "https://raw.githubusercontent.com/leanhhu061206/LIVETV/main"

LIVETV_SOURCES = [
    "dlhd.m3u",
    "eventi_dlhd.m3u",
    "sports99.m3u",
    "sportsonline.m3u",
    "static.m3u",
    "streamed.m3u",
    "vavoo.m3u",
    "world.m3u"
]

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        print(f"[*] Creazione directory di output: {OUTPUT_DIR}")
        os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_daddylive_channels():
    print(f"\n[DADDYLIVE] Scaricamento pagina canali da {DADDY_CHANNELS_URL}...")
    channels = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, come Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    try:
        response = requests.get(DADDY_CHANNELS_URL, headers=headers, timeout=15)
        if response.status_code == 200:
            html_content = response.text
            clean_html = re.sub(r'<br\s*/?>', '\n', html_content)
            clean_html = re.sub(r'<[^>]+>', ' ', clean_html)
            matches = re.finditer(r'([A-Za-z0-9\s\+\-\&]+?)\s+ID:\s*(\d+)', clean_html)
            
            for match in matches:
                channel_name = match.group(1).strip()
                channel_id = match.group(2).strip()
                channel_name = re.sub(r'\s+', ' ', channel_name)
                if len(channel_name) > 1 and channel_name.lower() != "all" and not channel_name.isspace():
                    if not any(c['id'] == channel_id for c in channels):
                        channels.append({'id': channel_id, 'name': channel_name})
            return channels
    except Exception as e:
        print(f"[DADDYLIVE] Errore: {e}")
        return None

def generate_daddylive_m3u(channels):
    if not channels: return
    print(f"[DADDYLIVE] Generazione {DADDY_OUTPUT_FILE}...")
    try:
        with open(DADDY_OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for channel in channels:
                ch_id = channel.get("id", "")
                ch_name = channel.get("name", "Canale")
                
                original_url = f"{DADDY_DOMAIN}/stream/stream-{ch_id}.php"
                encoded_url = urllib.parse.quote(original_url, safe='')
                proxy_url = f"{EASYPROXY_BASE_URL}/extractor/video?d={encoded_url}&redirect_stream=true"
                
                f.write(f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{ch_name}" group-title="DaddyLive",{ch_name}\n')
                f.write(f'{proxy_url}\n')
    except IOError as e:
        print(f"Errore scrittura: {e}")

def process_livetv_sources():
    print(f"\n[LIVETV] Elaborazione sorgenti...")
    out_lines = ["#EXTM3U"]
    for source in LIVETV_SOURCES:
        raw_url = f"{LIVETV_RAW_BASE_URL}/{source}"
        try:
            response = requests.get(raw_url, timeout=15)
            if response.status_code == 200:
                for line in response.text.splitlines():
                    line = line.strip()
                    if line.startswith("#"):
                        if not line.upper().startswith("#EXTM3U"): out_lines.append(line)
                    elif line.startswith("http"):
                        encoded_url = urllib.parse.quote(line, safe='')
                        proxy_url = f"{EASYPROXY_BASE_URL}/proxy/manifest.m3u8?url={encoded_url}"
                        out_lines.append(proxy_url)
        except Exception as e:
            print(f"Errore {source}: {e}")
            
    try:
        with open(LIVETV_OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(out_lines) + "\n")
    except IOError as e: pass

def download_livetv_epg():
    epg_url = f"{LIVETV_RAW_BASE_URL}/epg.xml.gz"
    try:
        response = requests.get(epg_url, stream=True, timeout=20)
        if response.status_code == 200:
            with open(LIVETV_EPG_FILE, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192): f.write(chunk)
    except Exception: pass

def main():
    ensure_output_dir()
    daddy_channels = fetch_daddylive_channels()
    if daddy_channels: generate_daddylive_m3u(daddy_channels)
    process_livetv_sources()
    download_livetv_epg()

if __name__ == "__main__":
    main()
