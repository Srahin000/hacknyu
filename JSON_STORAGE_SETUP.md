# JSON Storage Setup (Hackathon Demo)

## Overview

For the hackathon demo, all data is stored in JSON files instead of a database. This makes setup simple and requires no external dependencies.

## Data Storage

### File Structure
```
conversations/
  └── YYYYMMDD/
      └── conv_XXXX_YYYYMMDD/
          ├── metadata.json
          ├── transcript.txt
          └── insights.json

dashboard_data/
  ├── stats.json          # Aggregate statistics
  ├── conversations.json  # All conversations
  └── dashboard.json      # Combined data

EDGEucatorDashboard/public/
  ├── stats.json          # Dashboard reads from here
  └── conversations.json  # Dashboard reads from here
```

## How It Works

### 1. Conversation Storage
- `harry_voice_assistant.py` saves conversations to `conversations/` directory
- `conversation_analyzer.py` analyzes and saves insights to JSON
- Each conversation gets its own directory with metadata, transcript, and insights

### 2. Dashboard Data Generation
- Run `python generate_dashboard_data.py` to aggregate all insights
- Creates `dashboard_data/` with:
  - `stats.json` - Aggregate statistics
  - `conversations.json` - All conversations
  - `dashboard.json` - Combined data
- Copy these files to `EDGEucatorDashboard/public/` for the dashboard

### 3. Dashboard Loading
- Dashboard API routes (`/api/stats`, `/api/conversations`) read from JSON files
- No database required - just file system access
- Works offline, perfect for demo

## Setup Steps

1. **Generate Dashboard Data**
   ```bash
   python generate_dashboard_data.py
   ```

2. **Copy to Dashboard**
   ```bash
   # Copy generated files to dashboard public folder
   copy dashboard_data\*.json EDGEucatorDashboard\public\
   ```

3. **Run Dashboard**
   ```bash
   cd EDGEucatorDashboard
   npm run dev
   ```

## Benefits for Hackathon

✅ **No Setup Required** - No database, no credentials  
✅ **Works Offline** - All data in local files  
✅ **Easy to Demo** - Just copy JSON files  
✅ **Fast** - Direct file reads, no network calls  
✅ **Portable** - Can zip and share entire project  

## Data Flow

```
Harry Assistant
    ↓
Saves to conversations/
    ↓
conversation_analyzer.py
    ↓
Generates insights.json
    ↓
generate_dashboard_data.py
    ↓
Creates dashboard_data/*.json
    ↓
Copy to EDGEucatorDashboard/public/
    ↓
Dashboard reads via /api/stats, /api/conversations
```

## Authentication

For the demo, authentication uses localStorage:
- Sign up/login stored in browser localStorage
- No server-side auth required
- Simple and works for demo purposes


