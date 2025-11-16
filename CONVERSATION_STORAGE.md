# Conversation Storage

The voice assistant automatically saves all conversations with audio files and transcripts.

## Storage Structure

All conversations are saved in the `conversations/` directory, organized by date:

```
conversations/
  └── YYYYMMDD/                    # Date folder (e.g., 20251115)
      └── conv_####_HHMMSS/        # Conversation folder
          ├── audio.wav            # Original audio recording
          ├── transcript.txt       # Human-readable transcript
          └── metadata.json       # Machine-readable metadata
```

## Example Structure

```
conversations/
  └── 20251115/
      ├── conv_0001_143022/
      │   ├── audio.wav
      │   ├── transcript.txt
      │   └── metadata.json
      ├── conv_0002_143145/
      │   ├── audio.wav
      │   ├── transcript.txt
      │   └── metadata.json
      └── conv_0003_150230/
          ├── audio.wav
          ├── transcript.txt
          └── metadata.json
```

## File Formats

### audio.wav
- **Format**: WAV (16-bit PCM)
- **Sample Rate**: 16,000 Hz
- **Channels**: Mono (1 channel)
- **Duration**: 8 seconds (or 6 seconds in test mode)

### transcript.txt
Human-readable text file containing:
```
Conversation #1
Timestamp: 2025-11-15 14:30:22
======================================================================

USER:
What is the meaning of life?

HARRY:
Well, that's a profound question! In the wizarding world, we believe...
```

### metadata.json
Machine-readable JSON file with complete conversation data:
```json
{
  "conversation_id": 1,
  "timestamp": "2025-11-15T14:30:22.123456",
  "date": "20251115",
  "time": "143022",
  "user_query": "What is the meaning of life?",
  "harry_response": "Well, that's a profound question! In the wizarding world...",
  "audio_file": "20251115/conv_0001_143022/audio.wav",
  "transcript_file": "20251115/conv_0001_143022/transcript.txt",
  "sample_rate": 16000,
  "audio_duration_seconds": 7.5,
  "stt_type": "whisper-npu",
  "tts_type": "xtts_v2",
  "wake_word_type": "picovoice"
}
```

## Metadata Fields

| Field | Description |
|-------|-------------|
| `conversation_id` | Sequential conversation number |
| `timestamp` | ISO 8601 timestamp |
| `date` | Date in YYYYMMDD format |
| `time` | Time in HHMMSS format |
| `user_query` | Transcribed user input |
| `harry_response` | Harry's AI-generated response |
| `audio_file` | Relative path to audio file |
| `transcript_file` | Relative path to transcript file |
| `sample_rate` | Audio sample rate (Hz) |
| `audio_duration_seconds` | Length of audio recording |
| `stt_type` | Speech-to-text type (`whisper-npu` or `whisper-cpu`) |
| `tts_type` | Text-to-speech type (`xtts_v2` or `pyttsx3`) |
| `wake_word_type` | Wake word detection type (`picovoice` or `keyboard`) |

## Usage

Conversations are automatically saved after each interaction. No configuration needed!

The system will:
1. ✅ Create date folders automatically
2. ✅ Save audio recordings in WAV format
3. ✅ Save transcripts in readable text format
4. ✅ Save metadata in JSON format
5. ✅ Organize by date and conversation number

## Accessing Saved Conversations

### View all conversations for a date:
```powershell
# List all conversations from today
Get-ChildItem conversations\20251115

# View a specific transcript
Get-Content conversations\20251115\conv_0001_143022\transcript.txt

# Listen to audio
Start-Process conversations\20251115\conv_0001_143022\audio.wav
```

### Parse metadata programmatically:
```python
import json
from pathlib import Path

# Load metadata
metadata_path = Path("conversations/20251115/conv_0001_143022/metadata.json")
with open(metadata_path) as f:
    metadata = json.load(f)

print(f"User asked: {metadata['user_query']']}")
print(f"Harry responded: {metadata['harry_response']}")
```

## Storage Location

By default, conversations are saved in:
- **Windows**: `C:\Users\<username>\Documents\HackNYU\conversations\`
- **Relative**: `./conversations/` (from project root)

## Notes

- Audio files are saved in WAV format for maximum compatibility
- Transcripts use UTF-8 encoding to support all characters
- Metadata uses JSON for easy parsing and integration
- Conversations are organized by date for easy browsing
- Each conversation gets a unique ID and timestamp

