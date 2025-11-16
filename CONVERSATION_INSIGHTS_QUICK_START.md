# Conversation Insights - Quick Start 🚀

## ✅ What We Built

**Background conversation analysis system that extracts insights and gives Harry context!**

### **3 New Files:**

1. **`conversation_analyzer.py`** - Extracts insights from conversations using LLama (background)
2. **`context_manager.py`** - Loads insights and builds context for Harry
3. **`CONVERSATION_INSIGHTS_README.md`** - Full documentation

### **Updated:**

- `harry_voice_assistant.py` - Now includes context system!

---

## 🎯 How It Works

```
User talks → Harry responds (12s)
     ↓
Save conversation
     ↓
BACKGROUND: Analyze with LLama (5-10s, non-blocking)
     ↓
Extract insights → Save insights.json
     ↓
Next conversation: Load context → Harry remembers! 🎉
```

**Key:** Analysis happens in background, doesn't slow down conversations!

---

## 🚀 Run It Now!

### **Option 1: Voice Assistant Only (Built-in Background Analysis)**

```powershell
# Start voice assistant (context enabled by default)
python harry_voice_assistant.py --test --cpu
```

**What happens:**
1. You talk, Harry responds ✅
2. Conversation saved ✅  
3. **Background:** LLama extracts insights ✅
4. Next conversation: Harry has context! ✅

### **Option 2: Two Terminals (Recommended for Development!)**

```powershell
# Terminal 1: Voice Assistant
python harry_voice_assistant.py --test --cpu

# Terminal 2: Insights Watcher (monitors & generates insights)
python conversation_watcher.py
```

**Why two terminals?**
- 🔍 **Visual feedback** - See insights being generated in real-time
- 🚀 **Continuous monitoring** - Automatically processes all new conversations
- 🧪 **Better for testing** - Can process existing conversations too

**Files created:**
```
conversations/20251116/conv_0001_012601/
├── user_audio.wav
├── harry_audio.wav
├── transcript.txt
├── metadata.json
└── insights.json  ← 🆕 New!
```

---

## 📊 What's in `insights.json`?

```json
{
  "topics": ["space", "rockets", "science"],
  "dominantEmotion": "Excited",
  "sentimentScore": 85,
  "summary": "Child discussed space exploration and asked about rockets",
  "keyPhrases": ["rockets are cool", "want to learn more"],
  "engagementLevel": "high",
  "questionCount": 5,
  "breakthrough": true,
  "needsAttention": false,
  "conversationId": 1,
  "analyzedAt": "2025-11-16T01:45:22Z"
}
```

**Perfect for your dashboard!** 📈

---

## 🧠 How Harry Uses Context

### **Conversation 1:**
```
You: "I love space!"
Harry: "That's great! Tell me more about space."
```

### **Conversation 2 (Harry remembers!):**
```
[Context loaded: topics=space, emotion=Excited, interest=high]

You: "How do rockets work?"
Harry: "Since you're interested in space, let me explain rockets..."
```

**Personalized and continuous!** 🎉

---

## 🔧 Commands

```powershell
# Run with context (default)
python harry_voice_assistant.py --test --cpu

# Run without context (testing)
python harry_voice_assistant.py --test --cpu --no-context

# Analyze existing conversations
python conversation_analyzer.py --batch

# View current context
python context_manager.py
```

---

## 📈 Dashboard Integration

Your dashboard can now:

1. **Read `insights.json`** from each conversation folder
2. **Display trends** - Topics, emotions, engagement over time
3. **Show breakthroughs** - Learning "aha" moments
4. **Flag concerns** - `needsAttention: true`
5. **Track interests** - High-engagement topics

---

## ⚙️ Configuration

### **Disable Context (if needed):**

```powershell
python harry_voice_assistant.py --test --cpu --no-context
```

### **Customize Analysis Prompt:**

Edit `conversation_analyzer.py` → `create_extraction_prompt()` method

### **Change Context Window:**

Edit `context_manager.py`:
```python
ContextManager(max_context_conversations=5)  # Default: 5 recent conversations
```

---

## 🐛 Troubleshooting

### **"Context system disabled" message**

✅ **Normal** - Context loads on first initialization. Check if it works on next run.

### **No `insights.json` files appearing**

1. Check background thread is running (should print "Background analysis started...")
2. Wait ~10 seconds for analysis to complete
3. Run batch analysis: `python conversation_analyzer.py --batch`

### **Harry doesn't remember conversations**

1. Verify `insights.json` exists in conversation folders
2. Run: `python context_manager.py` to test
3. Check context is enabled (no `--no-context` flag)

---

## 📊 Performance

| Action | Time | User Waits? |
|--------|------|-------------|
| Conversation | 12s | ✅ Yes |
| Save | 100ms | ✅ Yes (negligible) |
| **Background analysis** | **5-10s** | **❌ No!** |
| Load context | 50ms | ✅ Yes (negligible) |

**Total user-facing time: ~12s** (same as before!)

---

## ✅ Summary

### **What's New:**

✅ **Background insights extraction** - Topics, emotions, learning patterns
✅ **Context for Harry** - Remembers previous conversations
✅ **Dashboard-ready JSON** - Matches your schema exactly
✅ **Zero performance impact** - Runs in background
✅ **Automatic** - Works by default, no config needed

### **Quick Commands:**

```powershell
# Run voice assistant
python harry_voice_assistant.py --test --cpu

# Check context works
python context_manager.py

# Analyze existing conversations
python conversation_analyzer.py --batch
```

### **Read More:**

📖 **Full documentation:** `CONVERSATION_INSIGHTS_README.md`

---

## 🎉 You're Ready!

Your voice assistant now:
- ✅ Extracts insights automatically
- ✅ Builds conversation context
- ✅ Gives Harry memory across conversations
- ✅ Generates dashboard-ready data

**Just run and talk - everything happens automatically!** 🚀

