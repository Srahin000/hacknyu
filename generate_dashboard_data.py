"""
Generate Dashboard Data from Conversation Insights
Aggregates all conversation insights into JSON format for EDGEucator dashboard
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def load_all_insights(conversations_dir: Path = Path("conversations")):
    """Load all conversation insights from all dates, grouped by childId"""
    
    all_insights = []
    
    if not conversations_dir.exists():
        print(f"⚠️  Conversations directory not found: {conversations_dir}")
        return all_insights
    
    # Iterate through date directories
    for date_dir in sorted(conversations_dir.iterdir()):
        if not date_dir.is_dir():
            continue
        
        # Iterate through conversation directories
        for conv_dir in sorted(date_dir.iterdir()):
            if not conv_dir.is_dir() or not conv_dir.name.startswith("conv_"):
                continue
            
            insights_path = conv_dir / "insights.json"
            metadata_path = conv_dir / "metadata.json"
            
            if insights_path.exists():
                try:
                    with open(insights_path, 'r', encoding='utf-8') as f:
                        insight = json.load(f)
                    
                    # Add metadata if available
                    if metadata_path.exists():
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        insight['userQuery'] = metadata.get('user_query', '')
                        insight['harryResponse'] = metadata.get('harry_response', '')
                        insight['timestamp'] = metadata.get('timestamp', '')
                        insight['date'] = date_dir.name
                        insight['convDir'] = conv_dir.name
                        
                        # Ensure childId is set (use from metadata if not in insights)
                        if 'childId' not in insight:
                            insight['childId'] = metadata.get('childId', 'child-default')
                        if 'userId' not in insight:
                            insight['userId'] = metadata.get('userId', 'user-default')
                    
                    all_insights.append(insight)
                
                except Exception as e:
                    print(f"⚠️  Failed to load {insights_path}: {e}")
    
    return all_insights


def generate_dashboard_stats(insights, childId: str = None):
    """Generate comprehensive stats for dashboard, optionally filtered by childId"""
    
    # Filter by childId if provided
    if childId:
        insights = [i for i in insights if i.get('childId') == childId]
    
    if not insights:
        return {
            "error": "No insights found",
            "totalConversations": 0,
            "childId": childId
        }
    
    # Basic counts
    total_conversations = len(insights)
    total_questions = sum(i.get('questionCount', 0) for i in insights)
    total_breakthroughs = sum(1 for i in insights if i.get('breakthrough', False))
    attention_needed = sum(1 for i in insights if i.get('needsAttention', False))
    
    # Topic analysis
    topic_counts = defaultdict(int)
    for insight in insights:
        for topic in insight.get('topics', []):
            topic_counts[topic] += 1
    
    top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Emotion distribution
    emotion_counts = defaultdict(int)
    for insight in insights:
        emotion = insight.get('dominantEmotion', 'Neutral')
        emotion_counts[emotion] += 1
    
    # Sentiment analysis
    sentiments = [i.get('sentimentScore', 50) for i in insights]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 50
    
    # Engagement levels
    engagement_counts = defaultdict(int)
    for insight in insights:
        engagement = insight.get('engagementLevel', 'medium')
        engagement_counts[engagement] += 1
    
    # Timeline data (by date)
    timeline = defaultdict(lambda: {
        'count': 0,
        'avgSentiment': [],
        'breakthroughs': 0,
        'topics': set()
    })
    
    for insight in insights:
        date = insight.get('date', 'unknown')
        timeline[date]['count'] += 1
        timeline[date]['avgSentiment'].append(insight.get('sentimentScore', 50))
        if insight.get('breakthrough', False):
            timeline[date]['breakthroughs'] += 1
        for topic in insight.get('topics', []):
            timeline[date]['topics'].add(topic)
    
    # Process timeline
    timeline_data = []
    for date, data in sorted(timeline.items()):
        avg_sent = sum(data['avgSentiment']) / len(data['avgSentiment']) if data['avgSentiment'] else 50
        timeline_data.append({
            'date': date,
            'conversations': data['count'],
            'avgSentiment': round(avg_sent, 1),
            'breakthroughs': data['breakthroughs'],
            'topicsCount': len(data['topics'])
        })
    
    # Recent conversations (last 5)
    recent_conversations = []
    for insight in sorted(insights, key=lambda x: x.get('analyzedAt', ''), reverse=True)[:5]:
        recent_conversations.append({
            'id': insight.get('conversationId', 0),
            'date': insight.get('date', ''),
            'userQuery': insight.get('userQuery', '')[:100],
            'topics': insight.get('topics', [])[:3],
            'emotion': insight.get('dominantEmotion', 'Neutral'),
            'sentiment': insight.get('sentimentScore', 50),
            'engagement': insight.get('engagementLevel', 'medium'),
            'breakthrough': insight.get('breakthrough', False),
            'summary': insight.get('summary', '')[:200]
        })
    
    # Key phrases (most common)
    phrase_counts = defaultdict(int)
    for insight in insights:
        for phrase in insight.get('keyPhrases', []):
            phrase_counts[phrase] += 1
    
    top_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)[:15]
    
    return {
        'generatedAt': datetime.now().isoformat(),
        'summary': {
            'totalConversations': total_conversations,
            'totalQuestions': total_questions,
            'totalBreakthroughs': total_breakthroughs,
            'attentionNeeded': attention_needed,
            'avgSentiment': round(avg_sentiment, 1)
        },
        'topics': {
            'topTopics': [{'name': t, 'count': c} for t, c in top_topics],
            'totalUniqueTopics': len(topic_counts)
        },
        'emotions': {
            'distribution': dict(emotion_counts),
            'mostCommon': max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else 'Neutral'
        },
        'engagement': {
            'distribution': dict(engagement_counts),
            'high': engagement_counts.get('high', 0),
            'medium': engagement_counts.get('medium', 0),
            'low': engagement_counts.get('low', 0)
        },
        'timeline': timeline_data,
        'recentConversations': recent_conversations,
        'keyPhrases': [{'phrase': p, 'count': c} for p, c in top_phrases],
        'insights': {
            'breakthroughRate': round((total_breakthroughs / total_conversations * 100), 1) if total_conversations > 0 else 0,
            'avgQuestionsPerConversation': round(total_questions / total_conversations, 1) if total_conversations > 0 else 0,
            'attentionRate': round((attention_needed / total_conversations * 100), 1) if total_conversations > 0 else 0
        }
    }


def generate_conversation_list(insights, childId: str = None):
    """Generate detailed list of all conversations, optionally filtered by childId"""
    
    # Filter by childId if provided
    if childId:
        insights = [i for i in insights if i.get('childId') == childId]
    
    conversations = []
    
    for insight in sorted(insights, key=lambda x: x.get('analyzedAt', ''), reverse=True):
        conversations.append({
            'id': insight.get('conversationId', 0),
            'childId': insight.get('childId', 'child-default'),
            'userId': insight.get('userId', 'user-default'),
            'timestamp': insight.get('timestamp', ''),
            'date': insight.get('date', ''),
            'convDir': insight.get('convDir', ''),
            'userQuery': insight.get('userQuery', ''),
            'harryResponse': insight.get('harryResponse', ''),
            'summary': insight.get('summary', ''),
            'topics': insight.get('topics', []),
            'dominantEmotion': insight.get('dominantEmotion', 'Neutral'),
            'sentimentScore': insight.get('sentimentScore', 50),
            'engagementLevel': insight.get('engagementLevel', 'medium'),
            'questionCount': insight.get('questionCount', 0),
            'breakthrough': insight.get('breakthrough', False),
            'needsAttention': insight.get('needsAttention', False),
            'keyPhrases': insight.get('keyPhrases', []),
            'analyzedAt': insight.get('analyzedAt', '')
        })
    
    return conversations


def main():
    """Main function to generate all dashboard data"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate dashboard data from conversation insights")
    parser.add_argument('--child-id', type=str, help='Filter by specific childId')
    parser.add_argument('--per-child', action='store_true', help='Generate separate files for each child')
    args = parser.parse_args()
    
    print("="*70)
    print(" Dashboard Data Generator ".center(70))
    print("="*70)
    print()
    
    # Load all insights
    print("📚 Loading conversation insights...")
    insights = load_all_insights()
    print(f"   Found {len(insights)} conversations with insights")
    print()
    
    if not insights:
        print("❌ No insights found!")
        print("   Run conversations first, then generate insights:")
        print("   python conversation_analyzer.py --batch")
        return
    
    # Group by childId
    child_groups = defaultdict(list)
    for insight in insights:
        childId = insight.get('childId', 'child-default')
        child_groups[childId].append(insight)
    
    print(f"   Found {len(child_groups)} children")
    for childId, child_insights in child_groups.items():
        print(f"     - {childId}: {len(child_insights)} conversations")
    print()
    
    # Create output directory
    output_dir = Path("dashboard_data")
    output_dir.mkdir(exist_ok=True)
    
    if args.per_child:
        # Generate separate files for each child
        for childId, child_insights in child_groups.items():
            print(f"📊 Generating stats for {childId}...")
            stats = generate_dashboard_stats(child_insights, childId=childId)
            
            print(f"📝 Generating conversation list for {childId}...")
            conversations = generate_conversation_list(child_insights, childId=childId)
            
            # Save per-child files
            child_output_dir = output_dir / childId
            child_output_dir.mkdir(exist_ok=True)
            
            stats_file = child_output_dir / "stats.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            print(f"✅ Stats saved: {stats_file}")
            
            conversations_file = child_output_dir / "conversations.json"
            with open(conversations_file, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, indent=2, ensure_ascii=False)
            print(f"✅ Conversations saved: {conversations_file}")
            
            combined_file = child_output_dir / "dashboard.json"
            combined = {
                'stats': stats,
                'conversations': conversations
            }
            with open(combined_file, 'w', encoding='utf-8') as f:
                json.dump(combined, f, indent=2, ensure_ascii=False)
            print(f"✅ Combined data saved: {combined_file}")
            print()
    
    # Generate overall stats (filtered if childId specified)
    if not args.per_child:
        print("📊 Generating overall dashboard statistics...")
        stats = generate_dashboard_stats(insights, childId=args.child_id)
        
        # Generate conversation list
        print("📝 Generating conversation list...")
        conversations = generate_conversation_list(insights, childId=args.child_id)
        
        # Save stats
        stats_file = output_dir / "stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Stats saved: {stats_file}")
        
        # Save conversation list
        conversations_file = output_dir / "conversations.json"
        with open(conversations_file, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Conversations saved: {conversations_file}")
        
        # Save combined data
        combined_file = output_dir / "dashboard.json"
        combined = {
            'stats': stats,
            'conversations': conversations
        }
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(combined, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Combined data saved: {combined_file}")
    
    # Print summary
    print()
    print("="*70)
    print(" Summary ".center(70))
    print("="*70)
    print(f"\n📊 Total Conversations: {stats['summary']['totalConversations']}")
    print(f"💬 Total Questions: {stats['summary']['totalQuestions']}")
    print(f"🎉 Breakthroughs: {stats['summary']['totalBreakthroughs']}")
    print(f"⚠️  Attention Needed: {stats['summary']['attentionNeeded']}")
    print(f"😊 Avg Sentiment: {stats['summary']['avgSentiment']}/100")
    print(f"\n🎯 Top Topics:")
    for topic in stats['topics']['topTopics'][:5]:
        print(f"   - {topic['name']}: {topic['count']} times")
    print(f"\n😊 Emotions:")
    for emotion, count in sorted(stats['emotions']['distribution'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   - {emotion}: {count}")
    
    print()
    print("="*70)
    print("\n✅ Dashboard data generated successfully!")
    print(f"\n📂 Files created in: {output_dir}/")
    print("   - stats.json (aggregate statistics)")
    print("   - conversations.json (all conversations)")
    print("   - dashboard.json (combined data)")
    
    # Stats saved to JSON file (for hackathon demo)
    
    print()
    print("🚀 Next steps:")
    print("   1. Copy dashboard_data/ to your EDGEucator Web App")
    print("   2. Integrate with Vite frontend")
    print("   3. Display stats in dashboard components")
    print()
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚡ Cancelled.\n")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

