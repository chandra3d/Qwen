# Blender AI Copilot

Multimodal Desktop AI Copilot for Blender - Sebuah asisten AI yang memahami konteks kerja pengguna Blender secara real-time melalui integrasi langsung dengan Blender API, screen capture, voice, keyboard, dan mouse.

## 🎯 Fitur Utama

- **Screen Capture** - Menangkap layar dengan adaptive FPS dan delta-frame optimization
- **Keyboard Tracking** - Mendeteksi shortcut Blender (Ctrl+R untuk loop cut, dll)
- **Mouse Tracking** - Melacak posisi, klik, dan drag operations
- **Voice Recording** - Transkripsi suara real-time dengan Faster-Whisper
- **Blender Integration** - Membaca state internal Blender secara langsung
- **Context Fusion Engine** - Menggabungkan semua input menjadi semantic context
- **Session Memory** - Menyimpan session dalam Universal AI Session Format

## 📋 Persyaratan Sistem

- **OS:** Windows 10 atau lebih baru
- **Blender:** Minimum versi 4.5
- **Python:** 3.10 atau lebih baru (untuk backend)
- **RAM:** Minimal 8GB (16GB direkomendasikan)
- **Storage:** 5GB free space

## 🚀 Instalasi

### Quick Install (Windows)

1. Download installer terbaru dari [Releases](https://github.com/your-repo/blender-copilot/releases)
2. Jalankan `BlenderAICopilot-Setup.exe`
3. Installer akan:
   - Install backend service
   - Install Blender add-on otomatis
   - Membuat shortcut desktop
4. Buka Blender, add-on sudah tersedia di sidebar (N) > tab "AI Copilot"

### Manual Install

#### 1. Install Backend Dependencies

```bash
cd blender-copilot
pip install -r requirements.txt
```

#### 2. Install Blender Add-on

1. Zip folder `src/blender_addon`
2. Di Blender: Edit > Preferences > Add-ons > Install
3. Pilih file zip yang dibuat
4. Enable add-on "AI Copilot"

#### 3. Jalankan Backend

```bash
python src/backend/main.py
```

#### 4. Connect dari Blender

1. Buka panel AI Copilot di sidebar Blender (tekan N)
2. Klik "Connect to Backend"
3. Status akan berubah menjadi "Connected"

## 📁 Struktur Proyek

```
blender-copilot/
├── src/
│   ├── backend/              # Python FastAPI backend
│   │   ├── main.py           # Entry point
│   │   ├── services/         # Core services
│   │   │   ├── context_fusion.py
│   │   │   ├── screen_capture.py
│   │   │   ├── keyboard_hook.py
│   │   │   ├── mouse_tracking.py
│   │   │   └── voice_recording.py
│   │   └── models/           # Data models
│   │       └── session.py
│   ├── blender_addon/        # Blender Python add-on
│   │   ├── __init__.py
│   │   ├── operators.py
│   │   ├── panels.py
│   │   └── handlers.py
│   └── desktop_client/       # Tauri desktop app (TODO)
├── assets/                   # Icons, models, etc.
├── installer/                # Windows installer scripts
├── tests/                    # Unit & integration tests
├── requirements.txt
├── JOB_LIST.md               # Project tracking
└── README.md
```

## 🎮 Cara Menggunakan

### Basic Usage

1. **Start Backend** - Jalankan server backend
2. **Connect Blender** - Klik "Connect" di panel AI Copilot
3. **Work Normally** - Gunakan Blender seperti biasa
4. **AI Understanding** - AI akan memahami konteks Anda secara otomatis

### Keyboard Shortcuts yang Dideteksi

| Shortcut | Action |
|----------|--------|
| Ctrl+R | Loop Cut |
| Ctrl+B | Bevel |
| E | Extrude |
| G | Grab/Move |
| R | Rotate |
| S | Scale |
| Tab | Toggle Edit Mode |
| Shift+A | Add Menu |

### Voice Commands (Coming Soon)

- "Add a cube"
- "Switch to edit mode"
- "Apply subdivision surface"

## 🔧 Konfigurasi

### Backend Settings

Edit di Blender add-on preferences:
- **Host:** localhost (default)
- **Port:** 8000 (default)
- **Auto Connect:** Yes/No
- **Send Interval:** 1.0 detik (default)

### Model AI

Untuk menggunakan local LLM/VLM:
- Llama 3.1 (via Ollama)
- Qwen2.5-VL (untuk visual understanding)
- Faster-Whisper (base/small/medium/large)

## 📊 Universal AI Session Format

Session disimpan dalam format standar:

```
.session/
├── metadata.json         # Session info
├── timeline.jsonl        # Event timeline
├── audio/                # Voice recordings
├── frames/               # Screenshots
├── embeddings/           # Vector embeddings
└── blender_state/        # State snapshots
```

Format ini kompatibel dengan:
- Codex
- Claude Code
- Local LLM
- VLM
- Omni AI

## 🛠️ Development

### Running Tests

```bash
pytest tests/
```

### Building for Windows

```bash
# Build backend executable
pyinstaller --onefile src/backend/main.py

# Create installer
cd installer/windows
iscc blender_copilot_installer.iss
```

## 📝 Roadmap

- [x] Project setup & structure
- [x] Backend FastAPI server
- [x] Context Fusion Engine
- [x] Screen capture service
- [x] Keyboard hook service
- [x] Mouse tracking service
- [x] Voice recording service
- [x] Blender add-on skeleton
- [ ] Desktop client (Tauri)
- [ ] Local LLM integration
- [ ] VLM integration
- [ ] OCR integration
- [ ] Windows installer
- [ ] Testing & QA

## 🤝 Kontribusi

Silakan fork dan submit pull request!

## 📄 Lisensi

MIT License

---

**Vision:** AI ini nantinya terasa seperti "senior Blender artist yang duduk di samping pengguna dan melihat layar secara realtime."
