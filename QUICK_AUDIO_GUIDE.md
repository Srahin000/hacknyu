# Quick Audio Guide ⚡

## Where is my audio saved?

### ✅ TWO places at once!

#### 1️⃣ Single Folder: `audio/`
**All audio files in one place - easy access!**

```
audio/
├── user_20251116_203045_conv0001.wav     ← You
├── user_20251116_203045_conv0001.txt
├── harry_20251116_203048_conv0001.wav    ← Harry
├── harry_20251116_203048_conv0001.txt
└── ...
```

#### 2️⃣ Organized Folders: `conversations/`
**Organized by date and conversation - full context!**

```
conversations/
└── 20251116/
    ├── conv_0001_203045/
    │   ├── user_audio.wav         ← You
    │   ├── harry_audio.wav        ← Harry
    │   ├── transcript.txt         ← Full conversation
    │   └── metadata.json          ← Details
    └── conv_0002_203152/
        └── ...
```

## When to use which?

| Need | Use Folder |
|------|------------|
| **All audio files together** | `audio/` |
| **Export for ML training** | `audio/` |
| **Quick drag and drop** | `audio/` |
| **Find by date** | `conversations/` |
| **Full conversation context** | `conversations/` |
| **Metadata & debugging** | `conversations/` |

## File size?
- ~450 KB per conversation
- Saved in **both** locations = ~900 KB total per conversation
- 100 conversations ≈ 90 MB

## Delete old audio?
```powershell
# Delete audio older than 7 days
Get-ChildItem audio -File | Where {$_.CreationTime -lt (Get-Date).AddDays(-7)} | Remove-Item
```

## That's it! 
Run your voice assistant - all audio automatically saves to both places! 🎉

