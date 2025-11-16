# Audio File Organization

All audio files are now automatically saved and organized in the `conversations/` directory.

## Folder Structure

```
conversations/
├── tts_audio/                           # All Harry's voice responses
│   ├── harry_tts_20251116_203045_conv1.wav
│   ├── harry_tts_20251116_203045_conv1.txt
│   ├── harry_tts_20251116_203152_conv2.wav
│   ├── harry_tts_20251116_203152_conv2.txt
│   └── ...
│
└── conv_YYYYMMDD_HHMMSS_###/           # Individual conversations
    ├── user_audio.wav                  # Your recorded question
    ├── transcript.txt                  # What you said + Harry's text response
    └── metadata.json                   # Full conversation details
```

## File Naming Convention

### TTS Audio Files (Harry's Voice)
- **Format**: `harry_tts_YYYYMMDD_HHMMSS_conv###.wav`
- **Example**: `harry_tts_20251116_203045_conv1.wav`
- **Components**:
  - `YYYYMMDD`: Date (Year, Month, Day)
  - `HHMMSS`: Time (Hour, Minute, Second)
  - `conv###`: Conversation number in current session
- **Paired Text File**: Same name with `.txt` extension containing Harry's response text

### User Audio Files
- **Location**: Inside conversation folders
- **Format**: `conv_YYYYMMDD_HHMMSS_###/user_audio.wav`
- **Includes**: Your voice recording that was transcribed

## What Gets Saved

### For Every Conversation:
1. **Your Audio** → `conv_*/user_audio.wav` (16kHz WAV format)
2. **Transcription** → `conv_*/transcript.txt` (your question + Harry's response)
3. **Harry's Audio** → `tts_audio/harry_tts_*.wav` (TTS-generated speech)
4. **Harry's Text** → `tts_audio/harry_tts_*.txt` (response text)
5. **Metadata** → `conv_*/metadata.json` (timestamps, latencies, model info)

## Storage Details

- **TTS Audio Quality**: 22kHz WAV (XTTS v2 default)
- **User Audio Quality**: 16kHz mono WAV (Whisper input format)
- **Text Encoding**: UTF-8 (supports all characters)
- **No Automatic Cleanup**: Files persist until manually deleted

## Benefits

✅ **Review Conversations** - Listen to past interactions  
✅ **Debug Issues** - Check transcription accuracy  
✅ **Voice Training** - Use as dataset for custom voice models  
✅ **Backup History** - Keep record of all interactions  
✅ **Share Highlights** - Export interesting conversations  

## Disk Space Usage

Typical conversation:
- User audio (8 seconds): ~250 KB
- Harry TTS audio (5 seconds): ~200 KB
- Metadata + transcripts: ~2 KB
- **Total per conversation**: ~450 KB

Example: 100 conversations ≈ 45 MB

## Cleanup (Optional)

To clean up old conversations:

```powershell
# Delete conversations older than 7 days
Get-ChildItem conversations -Recurse | Where-Object {$_.CreationTime -lt (Get-Date).AddDays(-7)} | Remove-Item -Recurse -Force

# Delete all TTS audio but keep conversation folders
Remove-Item conversations\tts_audio\* -Force

# Delete everything (fresh start)
Remove-Item conversations\* -Recurse -Force
```

## Privacy Note

🔒 Audio files stay **100% local** on your device. They are never uploaded anywhere unless you explicitly share them.

