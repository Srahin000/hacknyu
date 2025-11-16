"""
Background Conversation Analyzer
Extracts insights from conversations using LLama (runs asynchronously)

After each conversation:
1. Load conversation metadata + transcript
2. Run LLama analysis (background thread)
3. Extract structured insights (topics, emotions, learning, etc.)
4. Save insights JSON
5. Update context for future conversations
"""

import json
import time
from pathlib import Path
from datetime import datetime
from threading import Thread
import sys

# Fix encoding
if sys.platform == 'win32':
    import io
    try:
        # Only wrap if not already wrapped and buffer exists
        if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except (AttributeError, ValueError):
        # If wrapping fails, just continue with the default stdout/stderr
        pass


class ConversationAnalyzer:
    """Analyzes conversations in background to extract insights"""
    
    def __init__(self, cpu_mode=False):
        """
        Initialize the analyzer with Genie LLM on NPU
        
        Args:
            cpu_mode: If True, skip analyzer (NPU is preferred, no CPU fallback)
        """
        print("🔍 Initializing Conversation Analyzer...")
        
        self.cpu_mode = cpu_mode
        self.llm = None
        
        # Load LLM for analysis (NPU Genie)
        try:
            from harry_llm_npu import HarryPotterNPU
            self.llm = HarryPotterNPU()
            print("  ✅ Analyzer ready (using Genie NPU)")
            
        except Exception as e:
            print(f"  ⚠️  Analyzer initialization failed: {e}")
            print("     Insights will not be extracted.")
            self.llm = None
    
    def create_extraction_prompt(self, metadata: dict, transcript: str) -> str:
        """
        Create prompt for LLama to extract insights
        
        Args:
            metadata: Conversation metadata
            transcript: Full transcript text
        
        Returns:
            Extraction prompt string
        """
        user_query = metadata.get('user_query', 'N/A')
        harry_response = metadata.get('harry_response', 'N/A')
        duration = metadata.get('audio_duration_seconds', 0)
        emotion = metadata.get('emotion', {})
        
        prompt = f"""You are analyzing a conversation between a child and Harry Potter (AI companion).

CONVERSATION DATA:
User said: "{user_query}"
Harry responded: "{harry_response}"
Duration: {duration} seconds
Detected emotion: {emotion.get('detected', 'unknown')}

YOUR TASK:
Extract the following insights and return them as valid JSON:

1. TOPICS: What subjects were discussed? (e.g., space, math, friends, art, school, family)
2. DOMINANT_EMOTION: Child's overall emotional state (one of: Joyful, Calm, Neutral, Frustrated, Anxious, Excited, Curious, Worried, Happy, Stressed)
3. SENTIMENT_SCORE: 0-100 (0-30=negative, 31-60=neutral, 61-100=positive)
4. SUMMARY: 2-3 sentence neutral summary
5. KEY_PHRASES: Important phrases (de-identified, no real names)
6. ENGAGEMENT_LEVEL: "low", "medium", or "high"
7. QUESTION_COUNT: Number of questions the child asked
8. LEARNING_BREAKTHROUGH: Did child have an "aha" moment? true/false
9. NEEDS_ATTENTION: Should parent check in? true/false

Return ONLY valid JSON in this exact format:
{{
  "topics": ["topic1", "topic2"],
  "dominantEmotion": "Excited",
  "sentimentScore": 85,
  "summary": "Child discussed...",
  "keyPhrases": ["phrase1", "phrase2"],
  "engagementLevel": "high",
  "questionCount": 3,
  "breakthrough": false,
  "needsAttention": false
}}

Return ONLY the JSON, no other text."""

        return prompt
    
    def parse_llm_response(self, response: str) -> dict:
        """
        Parse LLM response into structured insights
        
        Args:
            response: Raw LLM response text
        
        Returns:
            Parsed insights dictionary
        """
        try:
            # Try to find JSON in response
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx+1]
                insights = json.loads(json_str)
                return insights
            else:
                print("  ⚠️  No JSON found in LLM response")
                return self.get_default_insights()
                
        except json.JSONDecodeError as e:
            print(f"  ⚠️  JSON parse error: {e}")
            return self.get_default_insights()
    
    def get_default_insights(self) -> dict:
        """Return default insights if extraction fails"""
        return {
            "topics": ["general conversation"],
            "dominantEmotion": "Neutral",
            "sentimentScore": 50,
            "summary": "Conversation with Harry Potter assistant.",
            "keyPhrases": [],
            "engagementLevel": "medium",
            "questionCount": 0,
            "breakthrough": False,
            "needsAttention": False
        }
    
    def analyze_conversation(self, conv_dir: Path):
        """
        Analyze a single conversation and extract insights
        
        Args:
            conv_dir: Path to conversation directory
        """
        print(f"\n🔍 Analyzing conversation: {conv_dir.name}")
        
        try:
            # Load metadata
            metadata_path = conv_dir / "metadata.json"
            if not metadata_path.exists():
                print("  ⚠️  No metadata.json found")
                return
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Load transcript
            transcript_path = conv_dir / "transcript.txt"
            if transcript_path.exists():
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    transcript = f.read()
            else:
                transcript = ""
            
            # Check if insights already exist
            insights_path = conv_dir / "insights.json"
            if insights_path.exists():
                print("  ✅ Insights already exist, skipping")
                return
            
            # Create extraction prompt
            prompt = self.create_extraction_prompt(metadata, transcript)
            
            # Run LLM analysis
            print("  🧠 Running LLM analysis...")
            start_time = time.time()
            
            if self.llm:
                response, latency = self.llm.ask_harry(prompt)
                print(f"  ✅ Analysis complete ({latency}ms)")
                
                # Parse insights
                insights = self.parse_llm_response(response)
            else:
                print("  ⚠️  No LLM available, using defaults")
                insights = self.get_default_insights()
            
            # Add metadata
            insights['analyzedAt'] = datetime.now().isoformat()
            insights['analysisLatencyMs'] = int((time.time() - start_time) * 1000)
            insights['conversationId'] = metadata.get('conversation_id', 0)
            
            # Save insights
            with open(insights_path, 'w', encoding='utf-8') as f:
                json.dump(insights, f, indent=2, ensure_ascii=False)
            
            print(f"  💾 Insights saved to: {insights_path.name}")
            print(f"     Topics: {', '.join(insights.get('topics', []))}")
            print(f"     Emotion: {insights.get('dominantEmotion', 'N/A')}")
            print(f"     Engagement: {insights.get('engagementLevel', 'N/A')}")
            
            if insights.get('breakthrough'):
                print("     🎉 BREAKTHROUGH DETECTED!")
            if insights.get('needsAttention'):
                print("     ⚠️  NEEDS PARENT ATTENTION")
            
        except Exception as e:
            print(f"  ❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
    
    def analyze_conversation_async(self, conv_dir: Path):
        """
        Analyze conversation in background thread
        
        Args:
            conv_dir: Path to conversation directory
        """
        thread = Thread(target=self.analyze_conversation, args=(conv_dir,), daemon=True)
        thread.start()
        # Don't wait for thread - it runs in background!
    
    def batch_analyze(self, conversations_root: Path = Path("conversations")):
        """
        Analyze all conversations that don't have insights yet
        
        Args:
            conversations_root: Root conversations directory
        """
        print("🔍 Batch analyzing conversations...")
        print("="*70)
        
        if not conversations_root.exists():
            print("  ⚠️  No conversations directory found")
            return
        
        # Find all conversation directories
        conv_dirs = []
        for date_dir in sorted(conversations_root.iterdir()):
            if date_dir.is_dir():
                for conv_dir in sorted(date_dir.iterdir()):
                    if conv_dir.is_dir() and conv_dir.name.startswith("conv_"):
                        conv_dirs.append(conv_dir)
        
        print(f"Found {len(conv_dirs)} conversations")
        print()
        
        # Analyze each
        analyzed = 0
        skipped = 0
        
        for conv_dir in conv_dirs:
            insights_path = conv_dir / "insights.json"
            
            if insights_path.exists():
                skipped += 1
                continue
            
            self.analyze_conversation(conv_dir)
            analyzed += 1
        
        print()
        print("="*70)
        print(f"✅ Batch analysis complete!")
        print(f"   Analyzed: {analyzed}")
        print(f"   Skipped (already had insights): {skipped}")
        print(f"   Total: {len(conv_dirs)}")


def main():
    """Test the analyzer"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze voice assistant conversations (using Genie NPU)")
    parser.add_argument('--batch', action='store_true', help='Batch analyze all conversations')
    parser.add_argument('--conv-dir', type=str, help='Analyze specific conversation directory')
    
    args = parser.parse_args()
    
    analyzer = ConversationAnalyzer(cpu_mode=False)  # Use NPU
    
    if args.batch:
        analyzer.batch_analyze()
    elif args.conv_dir:
        conv_dir = Path(args.conv_dir)
        analyzer.analyze_conversation(conv_dir)
    else:
        print("Usage:")
        print("  python conversation_analyzer.py --batch")
        print("  python conversation_analyzer.py --conv-dir conversations/20251116/conv_0001_012601")


if __name__ == "__main__":
    main()

