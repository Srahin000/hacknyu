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
        print("[ANALYZER] Initializing Conversation Analyzer...")
        
        self.cpu_mode = cpu_mode
        self.llm = None
        
        # Load LLM for analysis (NPU Genie)
        try:
            from harry_llm_npu import HarryPotterNPU
            self.llm = HarryPotterNPU()
            print("  [OK] Analyzer ready (using Genie NPU)")
            
        except Exception as e:
            print(f"  [WARN] Analyzer initialization failed: {e}")
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
        
        prompt = f"""Analyze this conversation and return ONLY valid JSON, no other text.

CONVERSATION:
User: "{user_query}"
Harry: "{harry_response}"
Duration: {duration} seconds
Emotion: {emotion.get('detected', 'unknown')}

Return this exact JSON structure:
{{
  "topics": ["topic1", "topic2"],
  "dominantEmotion": "Excited",
  "sentimentScore": 85,
  "summary": "Brief summary here",
  "keyPhrases": ["phrase1"],
  "engagementLevel": "high",
  "questionCount": 1,
  "breakthrough": false,
  "needsAttention": false
}}

Rules:
- topics: list of subjects (e.g., ["homework", "math", "school"])
- dominantEmotion: one of: Joyful, Calm, Neutral, Frustrated, Anxious, Excited, Curious, Worried, Happy, Stressed
- sentimentScore: 0-100 number (0-30=negative, 31-60=neutral, 61-100=positive)
- summary: 2-3 sentence summary
- keyPhrases: array of important phrases
- engagementLevel: "low", "medium", or "high"
- questionCount: number of questions asked
- breakthrough: true or false
- needsAttention: true or false

Return ONLY the JSON object, nothing else."""

        return prompt
    
    def parse_llm_response(self, response: str) -> dict:
        """
        Parse LLM response into structured insights
        
        Args:
            response: Raw LLM response text
        
        Returns:
            Parsed insights dictionary
        """
        if not response:
            print("  [WARN] Empty LLM response")
            return self.get_default_insights()
        
        # Log the raw response for debugging (first 500 chars)
        print(f"  [DEBUG] LLM response preview: {response[:500]}...")
        
        try:
            # Strategy 1: Try to find JSON object in response
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx+1]
                
                # Try to parse as-is
                try:
                    insights = json.loads(json_str)
                    # Validate required fields
                    if self._validate_insights(insights):
                        return insights
                except json.JSONDecodeError:
                    pass
                
                # Strategy 2: Try to clean up common issues
                # Remove markdown code blocks
                json_str = json_str.replace('```json', '').replace('```', '').strip()
                
                # Try parsing again
                try:
                    insights = json.loads(json_str)
                    if self._validate_insights(insights):
                        return insights
                except json.JSONDecodeError:
                    pass
                
                # Strategy 3: Try to extract JSON from lines
                lines = json_str.split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    line = line.strip()
                    if line.startswith('{'):
                        in_json = True
                    if in_json:
                        json_lines.append(line)
                    if line.endswith('}') and in_json:
                        break
                
                if json_lines:
                    try:
                        json_str = ' '.join(json_lines)
                        insights = json.loads(json_str)
                        if self._validate_insights(insights):
                            return insights
                    except json.JSONDecodeError:
                        pass
            
            # Strategy 4: Try to parse entire response as JSON
            try:
                insights = json.loads(response.strip())
                if self._validate_insights(insights):
                    return insights
            except json.JSONDecodeError:
                pass
            
            print("  [WARN] No valid JSON found in LLM response")
            print(f"  [DEBUG] Full response: {response[:1000]}")
            return self.get_default_insights()
                
        except Exception as e:
            print(f"  [WARN] JSON parse error: {e}")
            print(f"  [DEBUG] Response was: {response[:500]}")
            return self.get_default_insights()
    
    def _validate_insights(self, insights: dict) -> bool:
        """Validate that insights have required fields and fix common issues"""
        required_fields = ['topics', 'dominantEmotion', 'sentimentScore']
        if not all(field in insights for field in required_fields):
            return False
        
        # Fix common issues
        # 1. Remove duplicate topics
        if 'topics' in insights and isinstance(insights['topics'], list):
            insights['topics'] = list(dict.fromkeys(insights['topics']))  # Preserves order
        
        # 2. Ensure engagementLevel is valid
        if 'engagementLevel' in insights:
            valid_levels = ['low', 'medium', 'high']
            if insights['engagementLevel'] not in valid_levels:
                # Try to infer from emotion or sentiment
                emotion = insights.get('dominantEmotion', '').lower()
                sentiment = insights.get('sentimentScore', 50)
                if 'frustrated' in emotion or 'anxious' in emotion or 'worried' in emotion:
                    insights['engagementLevel'] = 'low'
                elif sentiment > 70 or 'excited' in emotion or 'curious' in emotion:
                    insights['engagementLevel'] = 'high'
                else:
                    insights['engagementLevel'] = 'medium'
        
        # 3. Ensure sentimentScore is a number
        if 'sentimentScore' in insights:
            try:
                insights['sentimentScore'] = int(insights['sentimentScore'])
                # Clamp to 0-100
                insights['sentimentScore'] = max(0, min(100, insights['sentimentScore']))
            except (ValueError, TypeError):
                insights['sentimentScore'] = 50
        
        # 4. Ensure questionCount is a number
        if 'questionCount' in insights:
            try:
                insights['questionCount'] = int(insights['questionCount'])
            except (ValueError, TypeError):
                insights['questionCount'] = 0
        
        # 5. Ensure boolean fields are boolean
        for bool_field in ['breakthrough', 'needsAttention']:
            if bool_field in insights:
                insights[bool_field] = bool(insights[bool_field])
        
        return True
    
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
        print(f"\n[ANALYZE] Analyzing conversation: {conv_dir.name}")
        
        try:
            # Load metadata
            metadata_path = conv_dir / "metadata.json"
            if not metadata_path.exists():
                print("  [WARN] No metadata.json found")
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
                print("  [SKIP] Insights already exist, skipping")
                return
            
            # Create extraction prompt
            prompt = self.create_extraction_prompt(metadata, transcript)
            
            # Run LLM analysis
            print("  [LLM] Running LLM analysis...")
            start_time = time.time()
            
            if self.llm:
                # Use a custom system prompt for analysis (not Harry Potter character)
                analysis_system_prompt = """You are an expert conversation analyst. 
Your job is to analyze conversations and extract structured insights.
Always return valid JSON format, no other text."""
                
                response, latency = self.llm.ask_harry(prompt, system_prompt=analysis_system_prompt)
                print(f"  [OK] Analysis complete ({latency}ms)")
                
                # Parse insights
                insights = self.parse_llm_response(response)
            else:
                print("  [WARN] No LLM available, using defaults")
                insights = self.get_default_insights()
            
            # Add metadata
            insights['analyzedAt'] = datetime.now().isoformat()
            insights['analysisLatencyMs'] = int((time.time() - start_time) * 1000)
            insights['conversationId'] = metadata.get('conversation_id', 0)
            
            # Add user/child IDs if available
            if 'userId' in metadata:
                insights['userId'] = metadata['userId']
            if 'childId' in metadata:
                insights['childId'] = metadata['childId']
            
            # Save insights
            with open(insights_path, 'w', encoding='utf-8') as f:
                json.dump(insights, f, indent=2, ensure_ascii=False)
            
            print(f"  [SAVED] Insights saved to: {insights_path.name}")
            print(f"     Topics: {', '.join(insights.get('topics', []))}")
            print(f"     Emotion: {insights.get('dominantEmotion', 'N/A')}")
            print(f"     Engagement: {insights.get('engagementLevel', 'N/A')}")
            
            if insights.get('breakthrough'):
                print("     [BREAKTHROUGH] BREAKTHROUGH DETECTED!")
            if insights.get('needsAttention'):
                print("     [ATTENTION] NEEDS PARENT ATTENTION")
            
            # Insights saved to JSON file (for hackathon demo)
            
        except Exception as e:
            print(f"  [ERROR] Analysis failed: {e}")
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
        print("[BATCH] Batch analyzing conversations...")
        print("="*70)
        
        if not conversations_root.exists():
            print("  [WARN] No conversations directory found")
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
        print(f"[OK] Batch analysis complete!")
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

