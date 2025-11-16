# Voice Assistant WebApp Integration

This guide explains how to use the voice assistant with the webapp avatar interface.

## Setup

### 1. Install Dependencies

```bash
# Install Python dependencies (including FastAPI)
pip install -r requirements.txt

# Install webapp dependencies (if not already done)
cd EDGEucatorWebApp
npm install
```

### 2. Start the Backend Server

The backend server controls the voice assistant process and provides status updates.

**Windows:**
```bash
start_voice_assistant_server.bat
```

**Or manually:**
```bash
python voice_assistant_server.py
```

The server will start on `http://localhost:8000`

### 3. Start the WebApp

In a separate terminal:

```bash
cd EDGEucatorWebApp
npm run dev
```

The webapp will start on `http://localhost:3000`

## Usage

1. **Open the webapp** in your browser: `http://localhost:3000`

2. **Click "Start Voice Assistant"** button
   - This will launch the Python voice assistant in the background
   - The status indicator will show "Starting..."

3. **Wait for the assistant to initialize**
   - Status will change to "Idle" when ready
   - The avatar will be in idle animation

4. **Say "Harry Potter"** (wake word) or press ENTER (if using keyboard mode)
   - Status will change to "Listening..."
   - Avatar will switch to listening animation

5. **Speak your question**
   - After 8 seconds of recording, the status will change to "Generating Response..."
   - Avatar stays in idle while generating

6. **Harry responds**
   - Status changes to "Talking"
   - Avatar switches to talking animation
   - Audio plays with lip-sync

7. **After response**
   - Status returns to "Idle"
   - Avatar returns to idle animation
   - Conversation count updates

8. **Click "Stop Voice Assistant"** when done
   - This will terminate the Python process

## Status Indicators

- **Stopped** (gray) - Voice assistant is not running
- **Starting...** (orange) - Voice assistant is initializing
- **Idle** (gray, pulsing) - Ready, waiting for wake word
- **Listening...** (blue, pulsing) - Recording your voice
- **Generating Response...** (purple, pulsing) - Processing with LLM
- **Talking** (green, pulsing) - Playing audio response

## Architecture

- **Backend Server** (`voice_assistant_server.py`): FastAPI server that manages the voice assistant process
- **WebApp** (`EDGEucatorWebApp/`): React/Vite frontend with Three.js avatar
- **Voice Assistant** (`harry_voice_assistant.py`): Main Python script with WebSocket server
- **WebSocket Communication**: Real-time state updates between Python and webapp

## Troubleshooting

### "Failed to start voice assistant"
- Make sure the backend server is running on port 8000
- Check that all Python dependencies are installed
- Verify `harry_voice_assistant.py` exists and is executable

### Avatar not responding to states
- Check browser console for WebSocket connection errors
- Verify WebSocket server is running on port 8765
- Make sure the webapp is connected (check status indicator)

### Status not updating
- Check that status polling is active (should poll every second)
- Verify the backend server can access conversation metadata files
- Check browser console for API errors

## API Endpoints

- `GET /api/status` - Get current assistant status
- `POST /api/start` - Start the voice assistant
- `POST /api/stop` - Stop the voice assistant

## WebSocket Messages

The voice assistant broadcasts:
- `{type: 'state', state: 'idle'|'listening'|'talking', internal_state: 'generating'|...}` - State changes
- `{type: 'audio', url: '/audio/...'}` - Audio file URL for playback

