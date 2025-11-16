# Audio Storage - Dual Location System

All audio files are saved in **TWO locations** simultaneously:
1. ✅ **Single `audio/` folder** - All files together (easy access)
2. ✅ **Organized `conversations/` folders** - By date and conversation (structured)

## 📁 Folder Structure

```
audio/                                    ← ALL AUDIO FILES IN ONE PLACE
├── user_20251116_203045_conv0001.wav    ← Your voice recording
├── user_20251116_203045_conv0001.txt    ← Transcript
├── harry_20251116_203048_conv0001.wav   ← Harry's response audio
├── harry_20251116_203048_conv0001.txt   ← Harry's response text
├── user_20251116_203152_conv0002.wav
├── user_20251116_203152_conv0002.txt
├── harry_20251116_203155_conv0002.wav
├── harry_20251116_203155_conv0002.txt
└── ...

conversations/                            ← ORGANIZED BY DATE & CONVERSATION
├── 20251116/                             ← Today's date
│   ├── conv_0001_203045/                 ← Conversation #1
│   │   ├── user_audio.wav                ← Your recording (copy)
│   │   ├── harry_audio.wav               ← Harry's response (copy)
│   │   ├── transcript.txt                ← Full conversation text
│   │   ├── harry_response.txt            ← Harry's response text
│   │   └── metadata.json                 ← Conversation details
│   │
│   ├── conv_0002_203152/                 ← Conversation #2
│   │   ├── user_audio.wav
│   │   ├── harry_audio.wav
│   │   ├── transcript.txt
│   │   ├── harry_response.txt
│   │   └── metadata.json
│   └── ...
│
└── 20251117/                             ← Tomorrow's date
    └── ...
```

## 🎯 Use Cases

### Need All Audio Files Together?
→ Use `audio/` folder
- Great for: batch processing, training datasets, quick export
- Simple naming: `user_*` and `harry_*` prefixed files
- Chronological order by filename

### Need Organized Conversations?
→ Use `conversations/` folder
- Great for: reviewing specific conversations, debugging, metadata
- Organized by: date → conversation number
- Includes: audio + transcripts + metadata

## 📝 File Naming Convention

### In `audio/` Folder:
```
user_YYYYMMDD_HHMMSS_conv####.wav    - Your voice recording
user_YYYYMMDD_HHMMSS_conv####.txt    - Full transcript
harry_YYYYMMDD_HHMMSS_conv####.wav   - Harry's TTS audio
harry_YYYYMMDD_HHMMSS_conv####.txt   - Harry's text response
```

Example:
- `user_20251116_203045_conv0001.wav` = User recording, Nov 16 2025, 8:30:45 PM, conversation #1
- `harry_20251116_203048_conv0001.wav` = Harry's response, 3 seconds later

### In `conversations/YYYYMMDD/conv_####_HHMMSS/` Folders:
```
user_audio.wav        - Your voice recording
harry_audio.wav       - Harry's TTS audio
transcript.txt        - Full conversation (both user & Harry)
harry_response.txt    - Just Harry's response text
metadata.json         - Conversation metadata
```

## 💾 What Gets Saved

For **EVERY conversation**, you get:

| File | Location 1: `audio/` | Location 2: `conversations/` |
|------|---------------------|------------------------------|
| **Your voice** | `user_*_conv####.wav` | `YYYYMMDD/conv_####/user_audio.wav` |
| **Harry's voice** | `harry_*_conv####.wav` | `YYYYMMDD/conv_####/harry_audio.wav` |
| **Full transcript** | `user_*_conv####.txt` | `YYYYMMDD/conv_####/transcript.txt` |
| **Harry's text** | `harry_*_conv####.txt` | `YYYYMMDD/conv_####/harry_response.txt` |
| **Metadata** | ❌ (not saved) | `YYYYMMDD/conv_####/metadata.json` ✅ |

## 📊 Storage Details

### Audio Quality:
- **Your audio**: 16kHz mono WAV (Whisper input format)
- **Harry's audio**: 22kHz stereo WAV (XTTS v2 output)

### Disk Space (per conversation):
- Your recording (8 sec): ~250 KB
- Harry's response (5 sec): ~200 KB
- Transcripts + metadata: ~3 KB
- **Total**: ~450 KB × 2 locations = **~900 KB per conversation**

### Example Usage:
- 10 conversations: ~9 MB
- 100 conversations: ~90 MB
- 1000 conversations: ~900 MB

## 🧹 Cleanup Options

### Delete Old Audio (Keep Recent):
```powershell
# Delete from audio/ folder older than 7 days
Get-ChildItem audio -File | Where-Object {$_.CreationTime -lt (Get-Date).AddDays(-7)} | Remove-Item -Force
```

### Delete Just Organized Folders:
```powershell
# Keep audio/ but delete conversations/
Remove-Item conversations\* -Recurse -Force
```

### Delete Everything:
```powershell
# Fresh start - delete both folders
Remove-Item audio, conversations -Recurse -Force
```

### Keep Only Single Audio Folder:
```powershell
# Delete organized conversations, keep simple audio/ folder
Remove-Item conversations -Recurse -Force
```

## 🔒 Privacy

✅ **100% Local** - All audio stays on your device  
✅ **No Upload** - Nothing sent to cloud or internet  
✅ **You Control** - Delete anytime, no tracking  

## 🎨 Why Both Locations?

### Single `audio/` Folder:
- ⚡ **Fast access** - All files in one place
- 📦 **Easy export** - Drag and drop entire folder
- 🔍 **Simple search** - Chronological by filename
- 🤖 **ML training** - Perfect for datasets

### Organized `conversations/` Folders:
- 📅 **Date organization** - Find conversations by date
- 📝 **Rich metadata** - Full conversation context
- 🐛 **Debugging** - Includes model info, latencies
- 📊 **Analysis** - JSON metadata for processing

**Best of both worlds!** 🎉

