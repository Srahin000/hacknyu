# 🚀 Simple Avatar + Voice Assistant Setup

## The Flow
1. **Voice Assistant** runs in Terminal → broadcasts states via WebSocket
2. **Web App** shows avatar → connects to WebSocket → syncs states
3. **Audio** is saved to file → sent to avatar → plays with lip-sync

---

## Quick Start

### Terminal 1: Run Voice Assistant
```powershell
cd C:\Users\hackuser\Documents\HackNYU
python harry_voice_assistant.py
```

**What happens:**
- ✅ WebSocket server starts on `ws://localhost:8765`
- ✅ Loads Whisper (NPU), Harry AI (NPU), TTS
- ✅ Waits for "Harry Potter" wake word (or press ENTER if using keyboard mode)
- ⏱️  **Takes 30-60 seconds to load models** (be patient!)

### Terminal 2: Run Web App
```powershell
cd C:\Users\hackuser\Documents\HackNYU\EDGEucatorWebApp
npm run dev
```

**What happens:**
- Vite dev server starts on `http://localhost:3000`
- Avatar loads
- WebSocket client tries to connect to voice assistant
- **Note:** If voice assistant isn't ready yet, it will retry automatically

---

## How It Works

### States Flow:
1. **IDLE** → Avatar is idle, waiting for wake word
2. **LISTENING** → You said "Harry Potter", avatar listens
3. **GENERATING** → Harry AI is thinking (brief)
4. **TALKING** → Harry speaks, avatar talks with lip-sync
5. **IDLE** → Back to waiting

### Audio:
- Voice assistant saves audio to `audio/harry_TIMESTAMP.wav`
- Copies to `EDGEucatorWebApp/public/audio/` (for webapp access)
- Sends WebSocket message: `{ "type": "audio", "url": "/audio/harry_TIMESTAMP.wav" }`
- Webapp plays audio and animates avatar mouth

### Insights:
- After each conversation, insights auto-generate in background
- Saved to conversation folder: `conversations/YYYYMMDD/conv_XXXX/insights.json`
- Dashboard can read these insights

---

## Testing

### Test 1: Voice Assistant Alone
```powershell
cd C:\Users\hackuser\Documents\HackNYU
python harry_voice_assistant.py
```

Look for:
```
🌐 [0/5] Starting WebSocket server for avatar communication...
  ✅ WebSocket server ready on ws://localhost:8765

🔊 [1/4] Initializing Wake Word Detection...
  ✅ Wake word ready: 'Harry Potter' (Picovoice)
  
🎤 [2/4] Initializing Speech-to-Text...
  ✅ Using NPU Whisper (NPU (QNN Runtime))
  
🧠 [3/4] Initializing Harry Potter AI...
  ✅ Harry Potter AI loaded (Qualcomm Genie on NPU)
  
🔊 [5/5] Initializing Text-to-Speech...
  ✅ Text-to-Speech ready (pyttsx3)

======================================================================
                  🎯 VOICE ASSISTANT READY                   
======================================================================
```

Press ENTER (if using keyboard mode) and say something. Harry should respond.

### Test 2: Avatar Connection
1. Run voice assistant (Terminal 1)
2. Run webapp (Terminal 2): `npm run dev`
3. Open browser to `http://localhost:3000`
4. Check browser console for: `[WebSocket] Connected`
5. Avatar should show "Stopped" status initially

### Test 3: Full Flow
1. Voice assistant running
2. Webapp running
3. Press ENTER (or say "Harry Potter")
4. Avatar → **Listening** (animation changes)
5. Say: "Hello Harry, how are you?"
6. Avatar → **Generating** (brief)
7. Avatar → **Talking** (mouth animates with audio)
8. Avatar → **Idle** (back to idle)

---

## Troubleshooting

### WebSocket Connection Failed
**Symptom:** Browser console shows "WebSocket connection failed"
**Fix:** 
- Make sure voice assistant is running FIRST
- Wait 30-60 seconds for models to load
- Webapp will auto-retry connection every 5 seconds

### Voice Assistant Crashes on Startup
**Symptom:** Process exits immediately
**Possible causes:**
1. **Whisper models missing**: Check `models/whisper_base/` and `models/whisper_base2/` exist
2. **qai_hub_models not installed**: `pip install qai-hub-models`
3. **QNN SDK not found**: Check `C:\Qualcomm\AIStack\QAIRT\2.31.0.250130\` exists

### Audio Not Playing
**Symptom:** Avatar talks but no sound
**Check:**
1. Audio files exist in `EDGEucatorWebApp/public/audio/`
2. Browser console shows audio URL: `/audio/harry_TIMESTAMP.wav`
3. Audio file is valid (not empty)

### Avatar Not Changing States
**Symptom:** Avatar stays idle even when voice assistant is active
**Check:**
1. WebSocket connected? (browser console should show `[WebSocket] Connected`)
2. Voice assistant logs show: `[WebSocket] Broadcasting state: listening/talking`
3. Browser console shows: `[WebSocket] Avatar state changed to: listening/talking`

---

## Optional: Backend Server (Not Needed for Basic Setup)

If you want a start/stop button in the webapp:
```powershell
# Terminal 3 (instead of Terminal 1)
python voice_assistant_server.py
```

Then the webapp can start/stop the voice assistant via API.

**But for hackathon speed, just run manually!**

---

## File Locations

- **Conversations:** `conversations/YYYYMMDD/conv_XXXX/`
- **Insights:** `conversations/YYYYMMDD/conv_XXXX/insights.json`
- **Audio (voice assistant):** `audio/harry_TIMESTAMP.wav`
- **Audio (webapp):** `EDGEucatorWebApp/public/audio/harry_TIMESTAMP.wav`
- **Dashboard data:** `dashboard_data/stats.json`, `conversations.json`

---

## What's Auto-Generated

1. **After each conversation:**
   - `insights.json` (topics, emotions, sentiment, engagement)
   - Added to conversation folder

2. **To generate dashboard data:**
```powershell
python generate_dashboard_data.py
```

This creates:
- `dashboard_data/stats.json`
- `dashboard_data/conversations.json`
- `dashboard_data/child-default/stats.json` (per child)

---

## Ready to Demo! 🎉

1. Start voice assistant
2. Start webapp
3. Wait for models to load (~60 sec)
4. Press ENTER or say "Harry Potter"
5. Talk to Harry
6. Watch avatar sync perfectly!

**That's it! Simple, fast, hackathon-ready!**

