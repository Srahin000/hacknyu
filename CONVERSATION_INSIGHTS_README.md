# Conversation Insights System 🧠

## Overview

The voice assistant now has an intelligent conversation analysis system that:
1. **Runs in the background** (doesn't slow down conversations)
2. **Extracts insights** using LLama (topics, emotions, learning patterns)
3. **Feeds context to Harry** for personalized, continuous conversations

---

## 🔄 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    CONVERSATION FLOW                         │
└─────────────────────────────────────────────────────────────┘

1. User speaks → Harry responds                    [FAST! ~12s]
   ├─ Save conversation (audio + transcript)
   └─ Trigger background analysis ──┐
                                     │
2. Background Thread (async)         │◄─────────────┘
   ├─ Load conversation data
   ├─ Run LLama analysis              [~5-10s, doesn't block]
   ├─ Extract insights (JSON)
   └─ Save insights.json
   
3. Next Conversation
   ├─ Load recent insights
   ├─ Build context for Harry
   └─ Harry responds with personalization! 🎉
```

---

## 📊 What Insights Are Extracted

Each conversation is analyzed to extract:

### **Topics**
```json
["space", "rockets", "math", "friends"]
```

### **Emotions & Sentiment**
```json
{
  "dominantEmotion": "Excited",
  "sentimentScore": 85
}
```

### **Engagement Metrics**
```json
{
  "engagementLevel": "high",
  "questionCount": 5,
  "questionTypes": ["why", "how", "what-if"]
}
```

### **Learning Insights**
```json
{
  "struggleAreas": ["fractions"],
  "breakthroughMoments": ["understood rocket propulsion"],
  "skillsMentioned": ["coding", "reading"]
}
```

### **Flags**
```json
{
  "breakthrough": true,
  "needsAttention": false
}
```

---

## 🎯 How Harry Uses Context

When you start a new conversation, Harry automatically knows:

**Example Context Loaded:**
```
CONTEXT FROM PREVIOUS CONVERSATIONS:
- Last conversation: Child discussed space exploration and asked about rockets
- Recent topics: space, rockets, science, math, friends
- Emotional state: Excited (mood stable)
- Interests: space, coding, robots
- Recent breakthrough: understood rocket propulsion

CURRENT QUESTION: How do computers work?
```

**Harry's Response:**
> "That's a great question! You know how we talked about rockets earlier? Computers are 
> similar in that they follow instructions step by step. Since you're interested in 
> coding and robots, this will be really useful for you..."

**Personalized and continuous!** 🎉

---

## 📁 File Structure

After running conversations with insights enabled:

```
conversations/
├── 20251116/
│   ├── conv_0001_012601/
│   │   ├── user_audio.wav           # User's recording
│   │   ├── harry_audio.wav          # Harry's TTS
│   │   ├── transcript.txt           # Full conversation
│   │   ├── metadata.json            # Technical metadata
│   │   └── insights.json            # 🆕 Extracted insights!
│   │
│   ├── conv_0002_012845/
│   │   ├── user_audio.wav
│   │   ├── harry_audio.wav
│   │   ├── transcript.txt
│   │   ├── metadata.json
│   │   └── insights.json            # 🆕
│   ...
```

---

## 🚀 Usage

### **Option 1: Automatic (Enabled by Default)**

```powershell
# Context & insights enabled automatically!
python harry_voice_assistant.py --test --cpu
```

Every conversation:
1. Saves normally ✅
2. Triggers background analysis ✅
3. Next conversation uses context ✅

### **Option 2: Disable Context (For Testing)**

```powershell
python harry_voice_assistant.py --test --cpu --no-context
```

### **Option 3: Continuous Watcher (Recommended for Development)**

Run this in a **separate terminal** - it monitors for new conversations and auto-generates insights:

```powershell
# Terminal 1: Voice Assistant
python harry_voice_assistant.py --test --cpu

# Terminal 2: Insights Watcher (separate window)
python conversation_watcher.py
```

The watcher will:
- ✅ Detect new conversations automatically
- ✅ Generate insights in the background  
- ✅ Keep running continuously
- ✅ Skip conversations that already have insights

**Perfect for:** Testing, development, or running the assistant continuously!

### **Option 4: Batch Analyze Existing Conversations**

If you have conversations without insights:

```powershell
# Analyze all existing conversations (one-time)
python conversation_analyzer.py --batch
```

### **Option 5: Analyze Single Conversation**

```powershell
python conversation_analyzer.py --conv-dir conversations/20251116/conv_0001_012601
```

---

## 🔧 Components

### **1. ConversationAnalyzer** (`conversation_analyzer.py`)

- Runs LLama in background thread
- Extracts structured insights from conversations
- Saves `insights.json` files
- **Non-blocking!** Doesn't slow down conversations

**Key Methods:**
- `analyze_conversation(conv_dir)` - Analyze one conversation
- `analyze_conversation_async(conv_dir)` - Analyze in background thread
- `batch_analyze()` - Analyze all conversations

### **2. ContextManager** (`context_manager.py`)

- Loads recent insights
- Builds context for Harry
- Tracks topics, emotions, learning patterns
- Provides conversation summaries

**Key Methods:**
- `load_recent_insights(limit=5)` - Get recent insights
- `build_context_for_harry()` - Create context string for Harry
- `get_topic_history()` - Get all topics discussed
- `get_emotional_trend()` - Analyze emotional patterns
- `get_conversation_summary()` - Overall statistics

### **3. HarryVoiceAssistant** (`harry_voice_assistant.py`)

- **Updated** to integrate context system
- Automatically triggers background analysis after each conversation
- Loads context before asking Harry for a response

---

## 📈 Performance

| Component | Time | Blocking? | Impact |
|-----------|------|-----------|--------|
| **Conversation** | ~12s | Yes | User waits |
| **Save** | ~100ms | Yes | Negligible |
| **Background Analysis** | ~5-10s | **No** | Zero impact! |
| **Load Context** | ~50ms | Yes | Negligible |

**Total user-facing latency: ~12s** (same as before!)

The analysis happens in the background while you're thinking about your next question!

---

## 🎭 Example Conversation Flow

### **Conversation 1:**
```
User: "I love space and rockets!"
Harry: "That's wonderful! What do you want to learn about space?"

[Background: Analyzing...
 → Topics: ["space", "rockets"]
 → Emotion: "Excited"
 → Engagement: "high"
 → Saved to insights.json]
```

### **Conversation 2 (5 minutes later):**
```
[Context Loaded:
 - Last: discussed space and rockets
 - Emotion: Excited
 - Interest: space]

User: "How do rockets work?"
Harry: "Great question! I remember you're excited about space. 
       Rockets work by burning fuel..."
       
[Background: Analyzing...
 → Topics: ["space", "rockets", "science"]
 → Questions: ["how"]
 → Breakthrough: understood propulsion
 → Saved to insights.json]
```

### **Conversation 3 (next day):**
```
[Context Loaded:
 - Recent topics: space, rockets, science
 - Breakthrough: understood rocket propulsion
 - High interest: space]

User: "What do astronauts eat?"
Harry: "Since you've been learning about rockets and space exploration,
       you'll love this! Astronauts eat..."

[Background: Continuing to learn about you! 🚀]
```

---

## 🐛 Troubleshooting

### **"Context system disabled" error**

```powershell
# Install missing dependencies
pip install -r requirements.txt
```

### **"No insights found"**

Run batch analysis:
```powershell
python conversation_analyzer.py --batch
```

### **"Background analysis taking too long"**

- Analysis runs in background (doesn't block)
- Check `insights.json` appears in conversation folders
- LLama on CPU takes ~5-10s per conversation (normal)

### **"Harry doesn't seem to remember previous conversations"**

Check:
1. Are `insights.json` files being created?
2. Run: `python context_manager.py` to test
3. Make sure `enable_context=True` (default)

---

## 🎯 Dashboard Integration

The insights format matches your dashboard schema!

**Generated insights.json:**
```json
{
  "topics": ["space", "rockets"],
  "dominantEmotion": "Excited",
  "sentimentScore": 85,
  "summary": "Child discussed space exploration...",
  "keyPhrases": ["rockets are cool"],
  "engagementLevel": "high",
  "questionCount": 5,
  "breakthrough": true,
  "needsAttention": false,
  "analyzedAt": "2025-11-16T01:45:22.123Z",
  "conversationId": 1
}
```

**Your dashboard can:**
1. Read `insights.json` from each conversation
2. Display trends over time
3. Show breakthroughs and concerns
4. Track learning progress

---

## ✅ Summary

### **What You Get:**

✅ **Background Analysis** - Doesn't slow down conversations
✅ **Personalized Responses** - Harry remembers previous topics
✅ **Learning Insights** - Track breakthroughs and struggles
✅ **Emotional Awareness** - Detect mood changes
✅ **Dashboard Ready** - JSON format matches your schema
✅ **Zero Config** - Works automatically by default

### **Commands:**

```powershell
# Run voice assistant (context enabled)
python harry_voice_assistant.py --test --cpu

# Analyze existing conversations
python conversation_analyzer.py --batch

# View context and insights
python context_manager.py

# Disable context (testing)
python harry_voice_assistant.py --test --cpu --no-context
```

---

## 🚀 Next Steps

1. **Test it!** Run a few conversations and watch `insights.json` appear
2. **Check context** - Run `python context_manager.py`
3. **Integrate with dashboard** - Read `insights.json` files
4. **Customize prompts** - Edit extraction prompt in `conversation_analyzer.py`

**Your voice assistant now learns and grows with each conversation!** 🎉

