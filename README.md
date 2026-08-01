# 📺 EasyProxy IPTV Playlist Generator for Debrify

Generatore automatico di playlist IPTV M3U basato su **Python** e **GitHub Actions**.

Questo progetto effettua lo scraping dei canali live da **DaddyLive HD**, li instrada attraverso una propria istanza **EasyProxy** (ad esempio ospitata su **Koyeb**) e genera automaticamente un file `daddylive.m3u` aggiornato periodicamente ogni **6 ore**.

La playlist risultante è pronta per essere importata in **Debrify** oppure in qualsiasi player IPTV compatibile, come **TiviMate**, **Kodi**, **VLC** o **OTT Navigator**.

---

## ✨ Funzionalità principali

- 🔄 **Automazione 100% serverless** tramite GitHub Actions
- ⏰ Aggiornamento automatico ogni **6 ore**
- 🚀 Esecuzione manuale tramite `workflow_dispatch`
- 🛡️ **Bypass anti-bot e geoblocking** tramite EasyProxy
- 🔐 Gestione sicura delle credenziali con **GitHub Secrets**
- 📺 Playlist M3U compatibile con **Debrify** e player IPTV
- 🧩 Metadati `#EXTINF` puliti (`tvg-id`, `tvg-name`, `group-title`)
- ☁️ Nessun server personale da mantenere

---

## 🏗️ Architettura del sistema

```text
┌───────────────────────┐
│   DaddyLive HD Site   │  Scraping elenco canali
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ GitHub Actions (Cron) │  Esegue generate_playlists.py ogni 6 ore
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Repository GitHub     │  Aggiorna daddylive.m3u
└───────────┬───────────┘
            │ URL RAW
            ▼
┌───────────────────────┐
│ Debrify / IPTV Player │  Richiede lo stream M3U8
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ EasyProxy + Cloudflare│  Risolve e proxyfizza lo stream
└───────────────────────┘
```

---

## 📦 Prerequisiti

Prima di iniziare assicurati di avere:

- Un account **GitHub**
- Un'istanza **EasyProxy** funzionante (consigliato: Koyeb)
- **Cloudflare WARP** abilitato in EasyProxy (`/admin`)
- Python **3.11+** (solo per esecuzione locale)

> **Importante:** abilitare Cloudflare WARP riduce il rischio di blocchi IP da parte dei server di streaming.

---

## 🚀 Installazione

### 1. Clona il repository

```bash
git clone https://github.com/tuo-utente/iptv-auto-playlists.git
cd iptv-auto-playlists
```

Oppure crea un nuovo repository su GitHub e carica i file del progetto.

---

### 2. Configura la secret `EASYPROXY_URL`

Su GitHub vai in:

**Settings → Secrets and variables → Actions → New repository secret**

Inserisci:

| Campo | Valore |
|------|------|
| **Name** | `EASYPROXY_URL` |
| **Secret** | `https://tua-istanza.koyeb.app` |

⚠️ Non inserire lo slash finale `/`.

---

## 📁 Struttura del progetto

```text
.
├── generate_playlists.py
├── daddylive.m3u
└── .github
    └── workflows
        └── update_playlists.yml
```

| File | Descrizione |
|------|-------------|
| `generate_playlists.py` | Script principale di scraping e generazione M3U |
| `daddylive.m3u` | Playlist generata automaticamente |
| `update_playlists.yml` | Workflow GitHub Actions |

---

## 🐍 Script Python

Lo script utilizza la variabile d'ambiente `EASYPROXY_URL` per costruire gli URL proxy degli stream.

```python
import os
import requests

EASYPROXY_BASE_URL = os.environ.get(
    'EASYPROXY_URL',
    'https://tua-istanza-default.koyeb.app'
)

DADDY_OUTPUT_FILE = 'daddylive.m3u'
DADDY_DOMAIN = 'https://dlhd.st'
DADDY_CHANNELS_URL = f'{DADDY_DOMAIN}/24-7-channels.php'

# funzioni fetch_daddylive_channels()
# funzioni generate_daddylive_m3u()
```

Esecuzione locale:

```bash
export EASYPROXY_URL=https://tua-istanza.koyeb.app
python generate_playlists.py
```

---

## ⚙️ GitHub Actions

Crea il file `.github/workflows/update_playlists.yml`.

```yaml
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
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Installazione dipendenze
        run: pip install requests

      - name: Generazione playlist
        env:
          EASYPROXY_URL: ${{ secrets.EASYPROXY_URL }}
        run: python generate_playlists.py

      - name: Commit e push
        run: |
          git config --local user.email 'action@github.com'
          git config --local user.name 'GitHub Action Bot'

          git add *.m3u

          git commit -m 'Auto-aggiornamento lista M3U [skip ci]' || echo 'Nessuna modifica'

          git push
```

### Frequenza di aggiornamento

| Cron | Frequenza |
|------|------------|
| `0 */6 * * *` | Ogni 6 ore |

---

## ▶️ Primo avvio

1. Vai su **Actions** nel repository.
2. Seleziona **Aggiorna Lista M3U DaddyLive**.
3. Premi **Run workflow**.
4. Attendi il completamento del job.

Al termine comparirà il file `daddylive.m3u` aggiornato.

---

## 📺 Integrazione con Debrify

Dopo il primo aggiornamento:

1. Apri `daddylive.m3u` nel repository GitHub.
2. Clicca su **Raw**.
3. Copia l'URL mostrato nel browser.

Esempio:

```text
https://raw.githubusercontent.com/TUO_UTENTE/NOME_REPOSITORY/main/daddylive.m3u
```

4. Apri **Debrify → IPTV / Playlist M3U**.
5. Aggiungi una nuova sorgente e incolla l'URL.

La playlist verrà aggiornata automaticamente ogni 6 ore.

---

## 🔒 Sicurezza e privacy

### Repository pubblico

La playlist sarà accessibile pubblicamente tramite l'URL RAW.

### Repository privato

Per consentire a Debrify di leggere il file è necessario utilizzare un **Personal Access Token (PAT)** con permessi di lettura.

Esempio:

```text
https://raw.githubusercontent.com/UTENTE/REPOSITORY/main/daddylive.m3u?token=IL_TUO_PAT
```

### Protezione di EasyProxy

Per evitare utilizzi non autorizzati della tua istanza, configura la variabile d'ambiente:

```env
API_PASSWORD=una_password_sicura
```

direttamente nelle impostazioni del servizio EasyProxy.

---

## 🧪 Troubleshooting

### La playlist è vuota

- Verifica che DaddyLive sia raggiungibile.
- Controlla i log di GitHub Actions.

### Errore `EASYPROXY_URL not set`

Assicurati che la secret `EASYPROXY_URL` sia configurata correttamente.

### Gli stream non partono

- Verifica che EasyProxy sia online.
- Controlla che Cloudflare WARP sia attivo.

### GitHub Actions non effettua il push

Verifica che il workflow abbia:

```yaml
permissions:
  contents: write
```

---

## 🛠️ Personalizzazione

Puoi modificare:

- frequenza di aggiornamento (`cron`)
- nome del file M3U
- gruppi canali
- filtri sui canali
- sorgenti IPTV aggiuntive

---

## 📄 Licenza

Questo progetto è distribuito con licenza **MIT**. Consulta il file `LICENSE` per i dettagli.

---

## ⚠️ Disclaimer

Questo progetto è fornito esclusivamente a scopo **didattico e dimostrativo** per mostrare l'integrazione tra tecniche di scraping, proxy HLS e player IPTV.

L'utente è l'unico responsabile dell'utilizzo della playlist generata e dell'accesso ai contenuti tramite essa. Gli autori non ospitano, redistribuiscono né garantiscono la disponibilità dei flussi streaming di terze parti.

---

## ⭐ Supporto

Se il progetto ti è stato utile:

- lascia una ⭐ al repository
- apri una **Issue** per bug o suggerimenti
- contribuisci con una **Pull Request**
