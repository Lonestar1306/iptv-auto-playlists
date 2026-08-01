# daddylive-auto-m3u-scraper
📺 EasyProxy IPTV Playlist Generator for Debrify

Un sistema completamente automatizzato in Python e GitHub Actions che effettua lo scraping dei canali live da DaddyLive HD, li incapsula in un'istanza proxy personalizzata (EasyProxy su Koyeb) e genera un file .m3u aggiornato periodicamente ogni 6 ore.

La lista generata è pronta per essere importata direttamente in Debrify (o in qualsiasi lettore IPTV come TiviMate, Kodi o VLC), consentendo il bypass delle restrizioni geografiche e dei blocchi anti-bot senza caricare l'elaborazione sul client finale.

🚀 Caratteristiche Principali

Automazione 100% Serverless: Esecuzione programmata tramite GitHub Actions (ogni 6 ore o su richiesta via workflow_dispatch).

Bypass Anti-Bot e HLS Proxying: Integrazione diretta con EasyProxy per la risoluzione trasparente degli stream .m3u8 di DaddyLive HD.

Sicurezza delle credenziali: Supporto nativo per le GitHub Secrets per evitare di esporre l'URL o la chiave dell'istanza EasyProxy all'interno del codice sorgente.

Compatibilità Debrify: Formattazione metadati #EXTINF pulita (tvg-id, tvg-name) per la massima compatibilità con la griglia e il player nativo di Debrify.

🏗️ Architettura del Sistema

 ┌───────────────────────┐
 │   DaddyLive HD Site   │ (Scraping dell'elenco canali)
 └───────────┬───────────┘
             │
             ▼
 ┌───────────────────────┐
 │ GitHub Actions (Cron) │ ──► Esegue `generate_playlists.py` ogni 6 ore
 └───────────┬───────────┘
             │
             ▼
 ┌───────────────────────┐
 │ Repository GitHub     │ ──► Salva/aggiorna il file `daddylive.m3u`
 └───────────┬───────────┘
             │ (Import URL Raw)
             ▼
 ┌───────────────────────┐
 │ Debrify / IPTV Player │ ──► Invia richiesta HLS a EasyProxy (Koyeb)
 └───────────┬───────────┘
             │
             ▼
 ┌───────────────────────┐
 │ EasyProxy + Cloudflare│ ──► Risolve lo stream e restituisce il video
 └───────────────────────┘


🛠️ Guida all'Installazione e Configurazione

1. Prerequisiti

Un'istanza EasyProxy funzionante (ad es. ospitata su Koyeb).

Assicurarsi che Cloudflare WARP sia abilitato nel pannello /admin di EasyProxy (per prevenire blocchi IP sui server di streaming).

2. Configurazione del Repository GitHub

Clona o Crea un Repository (Pubblico o Privato):

git clone https://github.com/tuo-utente/iptv-auto-playlists.git
cd iptv-auto-playlists


Imposta la Secret dell'URL Proxy:

Vai su GitHub -> Settings -> Secrets and variables -> Actions.

Clicca su New repository secret.

Name: EASYPROXY_URL

Secret: https://tua-istanza.koyeb.app (senza slash finale /).

Struttura dei File da inserire:

generate_playlists.py: Lo script principale di generazione.

.github/workflows/update_playlists.yml: Il file di automazione per le GitHub Actions.

📜 Struttura dello Script Python (generate_playlists.py)

Lo script legge l'URL base dell'istanza dalla variabile d'ambiente EASYPROXY_URL ed estrae i canali tramite scraping HTML:

import os
import re
import sys
import urllib.parse
import requests

EASYPROXY_BASE_URL = os.environ.get(
    "EASYPROXY_URL", "https://tua-istanza-default.koyeb.app"
)
DADDY_OUTPUT_FILE = "daddylive.m3u"
DADDY_DOMAIN = "https://dlhd.st"
DADDY_CHANNELS_URL = f"{DADDY_DOMAIN}/24-7-channels.php"

# ... (funzioni fetch_daddylive_channels e generate_daddylive_m3u)


⏱️ Workflow GitHub Actions (.github/workflows/update_playlists.yml)

Il workflow pianificato esegue lo script e committa le modifiche al file .m3u solo se sono presenti aggiornamenti:

name: Aggiorna Lista M3U DaddyLive

on:
  workflow_dispatch:
  schedule:
    - cron: '0 */6 * * *'

permissions:
  contents: write

jobs:
  generate_playlists:
    runs-on: ubuntu-latest
    steps:
      - name: 1. Checkout repository
        uses: actions/checkout@v4

      - name: 2. Setup Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: 3. Installazione Dipendenze
        run: pip install requests

      - name: 4. Esecuzione Generatore
        env:
          EASYPROXY_URL: ${{ secrets.EASYPROXY_URL }}
        run: python generate_playlists.py

      - name: 5. Commit e Push su GitHub
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action Bot"
          git add *.m3u
          git commit -m "Auto-aggiornamento lista M3U [skip ci]" || echo "Nessuna modifica da salvare"
          git push


📺 Integrazione con Debrify

Una volta eseguito il primo workflow con successo, apri il file daddylive.m3u generato nella cartella del repository GitHub.

Clicca sul pulsante Raw per accedere al file di testo puro.

Copia l'URL dalla barra degli indirizzi:

https://raw.githubusercontent.com/<TUO_UTENTE>/<NOME_REPO>/main/daddylive.m3u


Apri Debrify, naviga alla sezione IPTV / Playlist M3U, aggiungi una nuova sorgente e incolla l'URL Raw.

🔒 Sicurezza e Privacy

Repository Privato: Se rendi il repository privato per nascondere il file .m3u, devi utilizzare un Personal Access Token (PAT) con permessi di lettura per consentire a Debrify di scaricare la lista:

https://raw.githubusercontent.com/<UTENTE>/<REPO>/main/daddylive.m3u?token=<IL_TUO_PAT>


Protezione EasyProxy: Per impedire a terzi di sfruttare la tua istanza Koyeb, valuta di configurare la variabile API_PASSWORD nelle impostazioni dell'ambiente del tuo server EasyProxy.

⚠️ Disclaimer

Questo progetto è sviluppato a scopo puramente didattico ed informativo per dimostrare l'interoperabilità tra sistemi di media extraction e lettori streaming. L'utente si assume la piena responsabilità dell'uso delle liste M3U e dei contenuti accessibili tramite di esse.
