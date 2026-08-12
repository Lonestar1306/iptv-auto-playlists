import urllib.parse
import json
import os
import sys
import re

try:
    import requests
except ImportError:
    print("[!] Errore: la libreria 'requests' non è installata.")
    print("[!] Installala eseguendo: pip install requests")
    sys.exit(1)

# ==========================================
# CONFIGURAZIONE GENERALE E DADDYLIVE
# ==========================================
# L'URL della tua istanza EasyProxy su Koyeb
EASYPROXY_BASE_URL = "https://breakable-brenn-piratescorporation-622824b8.koyeb.app"

# Parametri DaddyLive
DADDY_OUTPUT_FILE = "daddylive.m3u"
DADDY_DOMAIN = "https://dlhd.st"
DADDY_CHANNELS_URL = f"{DADDY_DOMAIN}/24-7-channels.php"

def fetch_daddylive_channels():
    """Recupera la lista canali tramite scraping della pagina pubblica di Daddylive."""
    print(f"\n[DADDYLIVE] Scaricamento pagina canali da {DADDY_CHANNELS_URL}...")
    channels = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, come Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
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
                        channels.append({
                            'id': channel_id,
                            'name': channel_name
                        })
                        
            return channels
        else:
            print(f"[DADDYLIVE] [!] Errore HTTP dal sito: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"[DADDYLIVE] [!] Errore di connessione a {DADDY_DOMAIN}: {e}")
        return None
    except Exception as e:
        print(f"[DADDYLIVE] [!] Errore inaspettato durante il parsing: {e}")
        return None

def generate_daddylive_m3u(channels):
    """Genera il file M3U formattato con EasyProxy per Daddylive."""
    if not channels:
        print("[DADDYLIVE] [-] Nessun canale recuperato.")
        return
        
    print(f"[DADDYLIVE] [*] Trovati {len(channels)} canali unici. Generazione {DADDY_OUTPUT_FILE}...")
    
    try:
        with open(DADDY_OUTPUT_FILE, "w", encoding="utf-8") as f:
            # Rimosso il doppio a capo, lasciamo una sola riga nuova
            f.write("#EXTM3U\n")
            
            for channel in channels:
                ch_id = channel.get("id", "")
                ch_name = channel.get("name", "Canale Sconosciuto")
                
                original_stream_url = f"{DADDY_DOMAIN}/stream/stream-{ch_id}.php"
                encoded_stream_url = urllib.parse.quote(original_stream_url, safe='')
                
                ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                encoded_ua = urllib.parse.quote(ua, safe='')
                
                # Utilizziamo l'endpoint HLS ottimizzato di EasyProxy
                proxy_url = f"{EASYPROXY_BASE_URL}/proxy/manifest.m3u8?url={encoded_stream_url}&h_User-Agent={encoded_ua}&h_Referer={DADDY_DOMAIN}/"
                
                # Aggiunto il parametro group-title e rimosso lo spazio dopo la virgola
                f.write(f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{ch_name}" group-title="DaddyLive",{ch_name}\n')
                # Rimosso il doppio a capo alla fine dell'URL
                f.write(f'{proxy_url}\n')
                
        print(f"[DADDYLIVE] [+] Lista generata con successo: {DADDY_OUTPUT_FILE}")
        
    except IOError as e:
        print(f"[DADDYLIVE] [!] Errore durante la scrittura del file: {e}")

def main():
    print("==================================================")
    print("   GENERATORE LISTA M3U DADDYLIVE (EASYPROXY)   ")
    print("==================================================")
    
    daddy_channels = fetch_daddylive_channels()
    if daddy_channels:
        generate_daddylive_m3u(daddy_channels)
    else:
        print("[DADDYLIVE] [-] Operazione fallita o saltata.")
        
    print("\n==================================================")
    print("Elaborazione completata.")
    print("==================================================")

if __name__ == "__main__":
    main()
