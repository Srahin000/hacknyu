"""
Conversation Watcher - Monitors for new conversations and generates insights

Run this in a separate terminal alongside the voice assistant:
    python conversation_watcher.py

It will:
1. Watch the conversations folder
2. Detect new conversations
3. Generate insights.json automatically
4. Keep running continuously
"""

import time
import sys
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
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

try:
    from conversation_analyzer import ConversationAnalyzer
except ImportError:
    print("❌ Could not import ConversationAnalyzer")
    print("   Make sure conversation_analyzer.py is in the same directory")
    sys.exit(1)


class ConversationWatcher:
    """Watches for new conversations and generates insights automatically"""
    
    def __init__(self, conversations_root: Path = Path("conversations"), check_interval: float = 5.0):
        """
        Initialize the watcher
        
        Args:
            conversations_root: Root directory for conversations
            check_interval: How often to check for new conversations (seconds)
        """
        self.conversations_root = conversations_root
        self.check_interval = check_interval
        self.processed_conversations = set()
        
        # Initialize the analyzer
        print("🔧 Initializing Conversation Analyzer...")
        self.analyzer = ConversationAnalyzer(cpu_mode=True)
        print("✅ Analyzer ready!\n")
        
        # Load already processed conversations
        self._load_existing_conversations()
    
    def _load_existing_conversations(self):
        """Load list of conversations that already have insights"""
        if not self.conversations_root.exists():
            return
        
        count = 0
        for date_dir in self.conversations_root.iterdir():
            if date_dir.is_dir():
                for conv_dir in date_dir.iterdir():
                    if conv_dir.is_dir() and conv_dir.name.startswith("conv_"):
                        insights_path = conv_dir / "insights.json"
                        if insights_path.exists():
                            self.processed_conversations.add(str(conv_dir))
                            count += 1
        
        print(f"📚 Found {count} conversations with existing insights")
        print(f"   (These will be skipped)\n")
    
    def _find_new_conversations(self):
        """Find conversations that need insights"""
        if not self.conversations_root.exists():
            return []
        
        new_conversations = []
        
        for date_dir in self.conversations_root.iterdir():
            if date_dir.is_dir():
                for conv_dir in date_dir.iterdir():
                    if conv_dir.is_dir() and conv_dir.name.startswith("conv_"):
                        conv_path_str = str(conv_dir)
                        
                        # Skip if already processed
                        if conv_path_str in self.processed_conversations:
                            continue
                        
                        # Check if metadata exists (conversation is complete)
                        metadata_path = conv_dir / "metadata.json"
                        if not metadata_path.exists():
                            continue
                        
                        # Check if insights already exist
                        insights_path = conv_dir / "insights.json"
                        if insights_path.exists():
                            self.processed_conversations.add(conv_path_str)
                            continue
                        
                        # This is a new conversation!
                        new_conversations.append(conv_dir)
        
        return new_conversations
    
    def watch(self):
        """Start watching for new conversations"""
        print("="*70)
        print("👀 CONVERSATION WATCHER STARTED")
        print("="*70)
        print(f"📁 Monitoring: {self.conversations_root.absolute()}")
        print(f"⏱️  Check interval: {self.check_interval}s")
        print(f"🧠 Analysis mode: CPU (Llama)")
        print("="*70)
        print("\n✨ Watching for new conversations... (Press Ctrl+C to stop)\n")
        
        try:
            while True:
                # Check for new conversations
                new_conversations = self._find_new_conversations()
                
                if new_conversations:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"\n[{timestamp}] 🆕 Found {len(new_conversations)} new conversation(s)")
                    
                    for conv_dir in new_conversations:
                        print(f"\n📂 {conv_dir.parent.name}/{conv_dir.name}")
                        print("   Generating insights...")
                        
                        # Analyze the conversation
                        self.analyzer.analyze_conversation(conv_dir)
                        
                        # Mark as processed
                        self.processed_conversations.add(str(conv_dir))
                        
                        print("   ✅ Done!\n")
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n\n" + "="*70)
            print("🛑 Watcher stopped by user")
            print("="*70)
            print(f"📊 Total conversations processed: {len(self.processed_conversations)}")
            print("👋 Goodbye!\n")


def main():
    """Run the watcher"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Watch for new conversations and generate insights")
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Check interval in seconds (default: 5.0)"
    )
    parser.add_argument(
        "--conversations-dir",
        type=str,
        default="conversations",
        help="Path to conversations directory (default: conversations)"
    )
    
    args = parser.parse_args()
    
    # Create and start watcher
    watcher = ConversationWatcher(
        conversations_root=Path(args.conversations_dir),
        check_interval=args.interval
    )
    watcher.watch()


if __name__ == "__main__":
    main()






