# Blender AI Copilot - Job List & Progress Tracker

## 📋 Project Overview
**Target Platform:** Windows 10+  
**Minimum Blender Version:** 4.5  
**Deployment:** Desktop Installer (.exe)

---

## ✅ Phase 1: Project Setup (COMPLETED)
- [x] Create folder structure
- [x] Initialize job tracking document

---

## 🔨 Phase 2: Core Backend Development
- [ ] **2.1** Setup Python backend with FastAPI
  - [ ] Create main.py entry point
  - [ ] Configure WebSocket support
  - [ ] Setup CORS for desktop client
- [ ] **2.2** Implement Screen Capture Service
  - [ ] DXGI integration for Windows
  - [ ] Adaptive FPS control
  - [ ] Delta-frame optimization
- [ ] **2.3** Implement Keyboard Hook Service
  - [ ] Global keyboard listener
  - [ ] Shortcut detection (Ctrl+R, etc.)
  - [ ] Key sequence logging
- [ ] **2.4** Implement Mouse Tracking Service
  - [ ] Mouse position tracking
  - [ ] Click/drag event detection
  - [ ] Viewport interaction mapping
- [ ] **2.5** Implement Voice Recording Service
  - [ ] Microphone input capture
  - [ ] Integration with Faster-Whisper
  - [ ] Real-time transcription
- [ ] **2.6** Build Context Fusion Engine
  - [ ] Multi-input data aggregation
  - [ ] Semantic context generation
  - [ ] Timeline event creation

---

## 🎨 Phase 3: Blender Add-on Development
- [ ] **3.1** Create Blender Add-on Structure
  - [ ] __init__.py with registration
  - [ ] Add-on preferences panel
  - [ ] Connection to backend service
- [ ] **3.2** Implement State Readers
  - [ ] Selected object info
  - [ ] Active mode detection
  - [ ] Modifiers list
  - [ ] Node editor state
  - [ ] Scene hierarchy
  - [ ] Geometry statistics
- [ ] **3.3** Implement Event Handlers
  - [ ] On selection change
  - [ ] On mode switch
  - [ ] On property update
  - [ ] On frame change
- [ ] **3.4** Create UI Panels in Blender
  - [ ] Copilot status panel
  - [ ] Quick actions
  - [ ] Settings configuration

---

## 🖥️ Phase 4: Desktop Client (Tauri/Electron)
- [ ] **4.1** Setup Desktop Framework (Tauri recommended)
  - [ ] Initialize Tauri project
  - [ ] Configure Rust backend
  - [ ] Setup React/Vue frontend
- [ ] **4.2** Build Main UI Components
  - [ ] Chat interface
  - [ ] Context visualization
  - [ ] Session timeline viewer
  - [ ] Settings panel
- [ ] **4.3** Implement WebSocket Client
  - [ ] Connect to backend
  - [ ] Real-time message handling
  - [ ] Reconnection logic
- [ ] **4.4** Integrate Local LLM/VLM
  - [ ] Model loader (Llama/Qwen)
  - [ ] VLM integration (Qwen2.5-VL)
  - [ ] Inference pipeline

---

## 💾 Phase 5: Memory & Session System
- [ ] **5.1** Implement Universal AI Session Format
  - [ ] metadata.json schema
  - [ ] timeline.jsonl structure
  - [ ] Audio storage
  - [ ] Frame storage
  - [ ] Embeddings storage
  - [ ] Blender state snapshots
- [ ] **5.2** Setup Database
  - [ ] SQLite for local storage
  - [ ] ChromaDB/LanceDB for embeddings
  - [ ] Query interface
- [ ] **5.3** Build Timeline Manager
  - [ ] Event logging
  - [ ] Context retrieval
  - [ ] Search functionality

---

## 🔌 Phase 6: Integration & Communication
- [ ] **6.1** Backend ↔ Blender Add-on Protocol
  - [ ] WebSocket communication
  - [ ] State sync mechanism
  - [ ] Command dispatching
- [ ] **6.2** Backend ↔ Desktop Client Protocol
  - [ ] Real-time updates
  - [ ] Query/Response pattern
  - [ ] Streaming support
- [ ] **6.3** OCR Integration
  - [ ] PaddleOCR/EasyOCR setup
  - [ ] UI element detection
  - [ ] Popup/menu parsing

---

## 📦 Phase 7: Windows Packaging & Deployment
- [ ] **7.1** Prepare Python Bundle
  - [ ] PyInstaller/Nuitka configuration
  - [ ] Include all dependencies
  - [ ] Optimize package size
- [ ] **7.2** Bundle Blender Add-on
  - [ ] Auto-installation script
  - [ ] Version compatibility check
- [ ] **7.3** Create Windows Installer
  - [ ] Inno Setup/NSIS script
  - [ ] Install Blender add-on automatically
  - [ ] Register startup services
  - [ ] Create desktop shortcuts
- [ ] **7.4** Test Installation on Clean Windows
  - [ ] Windows 10 clean VM test
  - [ ] Verify all components
  - [ ] Test with Blender 4.5+

---

## 🧪 Phase 8: Testing & QA
- [ ] **8.1** Unit Tests
  - [ ] Backend services
  - [ ] Blender operators
  - [ ] Utility functions
- [ ] **8.2** Integration Tests
  - [ ] End-to-end workflows
  - [ ] Multi-component scenarios
- [ ] **8.3** User Acceptance Testing
  - [ ] Real Blender workflow tests
  - [ ] Performance benchmarks
  - [ ] Memory/CPU usage analysis

---

## 🚀 Phase 9: Launch Preparation
- [ ] **9.1** Documentation
  - [ ] User guide
  - [ ] Installation instructions
  - [ ] API documentation
- [ ] **9.2** Release Build
  - [ ] Final installer build
  - [ ] Digital signing (optional)
  - [ ] Release notes
- [ ] **9.3** Distribution Setup
  - [ ] Download page
  - [ ] Update mechanism

---

## 📊 Current Status
**Phase:** 2 - Core Backend Development (COMPLETED)
**Progress:** 35%
**Last Updated:** Backend services & Blender add-on skeleton created

---

## ✅ Completed Tasks

### Phase 1: Project Setup
- [x] Create folder structure
- [x] Initialize job tracking document
- [x] Create README.md
- [x] Create requirements.txt
- [x] Create .gitignore

### Phase 2: Core Backend Development
- [x] **2.1** Setup Python backend with FastAPI
  - [x] Create main.py entry point
  - [x] Configure WebSocket support
  - [x] Setup CORS for desktop client
- [x] **2.2** Implement Screen Capture Service
  - [x] MSS integration for Windows
  - [x] Adaptive FPS control
  - [x] Delta-frame optimization
- [x] **2.3** Implement Keyboard Hook Service
  - [x] Global keyboard listener
  - [x] Shortcut detection (Ctrl+R, etc.)
  - [x] Key sequence logging
- [x] **2.4** Implement Mouse Tracking Service
  - [x] Mouse position tracking
  - [x] Click/drag event detection
  - [x] Viewport interaction mapping
- [x] **2.5** Implement Voice Recording Service
  - [x] Microphone input capture
  - [x] Integration with Faster-Whisper
  - [x] Real-time transcription
- [x] **2.6** Build Context Fusion Engine
  - [x] Multi-input data aggregation
  - [x] Semantic context generation
  - [x] Timeline event creation

### Phase 3: Blender Add-on Development
- [x] **3.1** Create Blender Add-on Structure
  - [x] __init__.py with registration
  - [x] Add-on preferences panel
  - [x] Connection to backend service
- [x] **3.2** Implement State Readers
  - [x] Selected object info
  - [x] Active mode detection
  - [x] Modifiers list
  - [x] Scene hierarchy
  - [x] Geometry statistics
- [x] **3.3** Implement Event Handlers
  - [x] On selection change
  - [x] On mode switch
  - [x] On property update
- [x] **3.4** Create UI Panels in Blender
  - [x] Copilot status panel
  - [x] Quick actions
  - [x] Settings configuration
- [x] Session Manager with Universal AI Session Format

---

## 🎯 Next Immediate Tasks

1. **Phase 4: Desktop Client (Tauri)** - Setup Tauri project dengan React frontend
2. **Phase 5: Memory & Session System** - Implementasi ChromaDB untuk embeddings
3. **Phase 6: Integration** - Testing koneksi end-to-end antara Blender dan backend
4. **Phase 7: Windows Packaging** - Setup PyInstaller dan Inno Setup untuk installer

---

## 📝 Catatan Penting

### Windows-Specific Dependencies
Beberapa modul hanya bekerja di Windows:
- `pywin32` - Windows API access
- `keyboard` - Global keyboard hook (requires admin on Windows)
- `mss` - Screen capture

### Blender Add-on Requirements
- Blender 4.5+ required
- Add-on location: `src/blender_addon/`
- Install via ZIP or copy to Blender addons folder

### Backend Service
- Runs on port 8000 by default
- WebSocket endpoints: `/ws/context`, `/ws/blender`
- REST API: `/api/session/*`, `/api/timeline/*`
