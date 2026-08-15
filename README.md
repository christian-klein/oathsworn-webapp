# Oathsworn: Into the Deepwood - Web Companion App

A browser-based companion for the board game [Oathsworn: Into the Deepwood](https://shadowborne-games.com/oathapp) by Shadowborne Games. It recreates the full in-app gamebook experience (chapter navigation, section text, narration audio, popup instructions, location tracking, time tracking, and more) accessible in any browser without needing a phone or Android emulator.

**This repo contains no copyrighted game content - not from the game or the app.**
All assets (audio, images, story text) are generated locally from the official game APK on your own machine and are never stored in this repository.

Getting the official APK to work on anything other than Bazzite + Waydroid was a huge pain for me (and it appears others).
Thus: let's make a web app.

---

## Quick Start (Docker & Docker Compose)

**Prerequisites:** Docker + Docker Compose (Linux, macOS, or Windows with WSL)

To build the self-contained container image and start the web app:

```bash
docker compose up -d
```

Or using `./setup.sh` / `make`:

```bash
./setup.sh                       # Builds oathsworn-webapp container image
docker compose up -d             # Starts web server at http://localhost:8080
```

Open **`http://localhost:8080`** in your browser.

---

## German Language Support

Set `INCLUDE_GERMAN_LANG=true` (or use `./setup.sh --german`) to also download the official German APK and generate German story text (`web/data/strings_de.js`). This enables German as a selectable story language in settings.

```bash
# With docker compose:
INCLUDE_GERMAN_LANG=true docker compose build

# With setup.sh:
./setup.sh --german

# With Makefile:
make build INCLUDE_GERMAN_LANG=true
```

---

## Features

### Multi-Stage Container & Media Optimizations
- **Self-Contained Docker Image**: Multi-stage build compiles `jadx` extraction, Python processing, Caddy web server, and web assets into a single portable Docker image (`oathsworn-webapp`).
- **Opus WebM Audio Compression**: Narration audio tracks are transcoded into **64 kbps Opus WebM (`.webm`)** format, reducing total audio storage from **1.5 GB $\rightarrow$ ~500 MB** (~66% reduction) with high-fidelity voice reproduction.
- **WebP Image Optimization**: Game illustrations and chapter images are transcoded into **WebP (`.webp`)**, shrinking image payloads by up to **90%**.
- **APK Caching**: Downloaded APK files are cached in `./cache/` so subsequent builds skip re-downloading.

### All 22 chapters supported
- All 21 numbered chapters plus Chapter 11.5
- Correct handling of two-path chapters (2, 5, 7, 9, 15) where the story splits into path A and path B
- Correct handling of Deepwood exploration chapters (4, 10, 14, 17, 18) with time token mechanics

### Gamebook experience
- Full section text and popup/event text displayed in reading order
- Chapter and section images displayed inline, capped to preserve proportions
- Image lightbox: click any image to zoom in full-screen; click or press Escape to close
- Hover highlight on images to indicate they are clickable
- Story choices and location buttons rendered at the bottom of each section
- Location buttons display the time token icon

### Audio narration
- Full narration audio for all sections that have it
- Multi-track support: sections with multiple audio clips show a track label and Prev/Next buttons
- Auto-play next track: when one track ends, the next plays automatically (configurable)
- Auto-start narration: audio begins playing when a new section loads (configurable)

### Auto-scroll
- Automatically scrolls through the story text in sync with narration
- Pauses when you scroll manually, with a tap-to-resume bar at the bottom
- Auto-scroll can be disabled in settings

### Time tracking
- Tracks cumulative time spent in each chapter
- Fires time-triggered story events and journal entries at the correct time values
- Correctly handles path-conditional time triggers (different redirects for path A vs path B players)

### Location tracking
- Tracks discovered locations and displays them as navigable buttons
- Supports adding, removing, and clearing locations as the story dictates

### Progress and saves
- Game progress saved automatically in browser localStorage per chapter
- **Backup & Restore Manager**: Export campaign progress and settings to `.json` files or import existing backups directly in the browser
- **Server Volume Snapshots**: Save, list, restore, and delete campaign snapshots stored on a mounted Docker volume (`/backups`) across devices
- Resume a chapter exactly where you left off
- Replay a completed chapter from the beginning (fully resets all chapter state)
- Chapter select screen shows In Progress / Completed status per chapter

### Chapter select screen
- Split-pane layout: chapter list on the left, detail panel on the right
- Chapter art and tagline shown in the detail panel
- Scroll indicators on the chapter list when there are more chapters above or below

### Language support
- Interface labels translated for English, German, Italian, and French (built-in, no extra setup)
- Language selector in Settings switches the app language at runtime
- Full story text translation: official German story text available via `./setup.sh --german`
- Fan-made story translations for other languages can be generated with the translation pipeline in `translations/` and dropped into `web/data/` as `strings_XX.js`

### Settings
- Persistent settings saved across sessions
- Toggle auto-scroll on/off
- Toggle auto-start narration on/off
- Toggle auto-play next audio track on/off
- Language selector: switch between any installed interface or story translations

### Scroll indicators
- Gradient overlay indicators on the choice/location button area when options are hidden off-screen
- Gradient overlay on the story text area that fades with scroll position
- Scroll indicators on the chapter list

### Might Decks
- Card draw assistant for combat encounters
- Tracks drawn cards, criticals, and critical chains across all four deck colors (White, Yellow, Red, Black)
- Left-click or right-click a deck card back to increase or decrease the draw count; mouse wheel also works
- Left-click or right-click the defense widget to adjust defense value; mouse wheel also works
- Draw More to add cards to the current result without clearing; disable individual cards to exclude them from the total
- Draw history tracks all draws for the session

### Bug reporting
- Built-in bug report button that captures current section, chapter, and full save state
- Pre-fills a report ready to copy and paste into a GitHub issue
