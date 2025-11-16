"""
Context Manager - Provides Harry with conversation history and insights

Loads recent insights and gives Harry context about:
- Previous topics discussed
- Child's interests and learning patterns
- Emotional state trends
- Breakthroughs and struggles
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class ContextManager:
    """Manages conversation context and insights for Harry"""
    
    def __init__(self, conversations_root: Path = Path("conversations"), max_context_conversations: int = 5):
        """
        Initialize context manager
        
        Args:
            conversations_root: Root directory for conversations
            max_context_conversations: Max number of recent conversations to include in context
        """
        self.conversations_root = conversations_root
        self.max_context = max_context_conversations
    
    def load_recent_insights(self, limit: int = None) -> List[Dict]:
        """
        Load recent conversation insights
        
        Args:
            limit: Max number of insights to load (default: self.max_context)
        
        Returns:
            List of insight dictionaries, newest first
        """
        if limit is None:
            limit = self.max_context
        
        insights = []
        
        if not self.conversations_root.exists():
            return insights
        
        # Collect all conversations with insights
        conversations = []
        for date_dir in sorted(self.conversations_root.iterdir(), reverse=True):
            if not date_dir.is_dir():
                continue
            
            for conv_dir in sorted(date_dir.iterdir(), reverse=True):
                if not conv_dir.is_dir() or not conv_dir.name.startswith("conv_"):
                    continue
                
                insights_path = conv_dir / "insights.json"
                metadata_path = conv_dir / "metadata.json"
                
                if insights_path.exists() and metadata_path.exists():
                    conversations.append({
                        'insights_path': insights_path,
                        'metadata_path': metadata_path,
                        'conv_dir': conv_dir
                    })
        
        # Load most recent insights
        for conv in conversations[:limit]:
            try:
                with open(conv['insights_path'], 'r', encoding='utf-8') as f:
                    insight = json.load(f)
                
                with open(conv['metadata_path'], 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Combine insights + key metadata
                combined = {
                    **insight,
                    'timestamp': metadata.get('timestamp'),
                    'user_query': metadata.get('user_query'),
                    'conversation_id': metadata.get('conversation_id')
                }
                
                insights.append(combined)
                
            except Exception as e:
                print(f"Warning: Failed to load insight from {conv['conv_dir']}: {e}")
                continue
        
        return insights
    
    def get_topic_history(self, limit: int = 10) -> List[str]:
        """
        Get list of unique topics discussed recently
        
        Args:
            limit: Max number of recent conversations to check
        
        Returns:
            List of unique topics
        """
        insights = self.load_recent_insights(limit=limit)
        
        topics = set()
        for insight in insights:
            for topic in insight.get('topics', []):
                topics.add(topic)
        
        return list(topics)
    
    def get_emotional_trend(self) -> Dict:
        """
        Get recent emotional trend
        
        Returns:
            Dict with dominant emotion and sentiment average
        """
        insights = self.load_recent_insights(limit=5)
        
        if not insights:
            return {
                'dominantEmotion': 'Neutral',
                'avgSentiment': 50,
                'trend': 'stable'
            }
        
        # Count emotions
        emotions = [i.get('dominantEmotion', 'Neutral') for i in insights]
        sentiments = [i.get('sentimentScore', 50) for i in insights]
        
        # Most common emotion
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        dominant = max(emotion_counts, key=emotion_counts.get)
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 50
        
        # Determine trend
        if len(sentiments) >= 3:
            recent_avg = sum(sentiments[:2]) / 2
            older_avg = sum(sentiments[2:]) / len(sentiments[2:])
            
            if recent_avg > older_avg + 10:
                trend = 'improving'
            elif recent_avg < older_avg - 10:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return {
            'dominantEmotion': dominant,
            'avgSentiment': round(avg_sentiment),
            'trend': trend
        }
    
    def get_learning_context(self) -> Dict:
        """
        Get learning-related context
        
        Returns:
            Dict with struggle areas, breakthroughs, and interests
        """
        insights = self.load_recent_insights(limit=10)
        
        struggles = []
        breakthroughs = []
        high_engagement_topics = []
        
        for insight in insights:
            # Collect struggles (if mentioned)
            if insight.get('sentimentScore', 50) < 40:
                struggles.extend(insight.get('topics', []))
            
            # Collect breakthroughs
            if insight.get('breakthrough'):
                breakthroughs.append({
                    'topic': ', '.join(insight.get('topics', [])),
                    'summary': insight.get('summary', '')
                })
            
            # High engagement topics
            if insight.get('engagementLevel') == 'high':
                high_engagement_topics.extend(insight.get('topics', []))
        
        return {
            'strugglingWith': list(set(struggles))[:3],  # Top 3
            'recentBreakthroughs': breakthroughs[:2],    # Last 2
            'highInterestTopics': list(set(high_engagement_topics))[:5]  # Top 5
        }
    
    def needs_attention_check(self) -> bool:
        """
        Check if any recent conversation flagged needs attention
        
        Returns:
            True if attention needed
        """
        insights = self.load_recent_insights(limit=3)
        
        for insight in insights:
            if insight.get('needsAttention'):
                return True
        
        return False
    
    def build_context_for_harry(self) -> str:
        """
        Build context string to prepend to Harry's prompt
        
        Returns:
            Context string with relevant information
        """
        insights = self.load_recent_insights(limit=3)
        
        if not insights:
            return ""
        
        # Build context summary
        topics = self.get_topic_history(limit=5)
        emotional = self.get_emotional_trend()
        learning = self.get_learning_context()
        
        context_parts = []
        
        # Recent conversation context
        if insights:
            most_recent = insights[0]
            context_parts.append(f"Last conversation: {most_recent.get('summary', 'N/A')}")
        
        # Topics
        if topics:
            context_parts.append(f"Recent topics: {', '.join(topics[:5])}")
        
        # Emotional state
        emotion_desc = emotional['dominantEmotion']
        if emotional['trend'] == 'improving':
            emotion_desc += " (mood improving)"
        elif emotional['trend'] == 'declining':
            emotion_desc += " (seems down lately)"
        
        context_parts.append(f"Emotional state: {emotion_desc}")
        
        # Learning context
        if learning['highInterestTopics']:
            context_parts.append(f"Interests: {', '.join(learning['highInterestTopics'][:3])}")
        
        if learning['strugglingWith']:
            context_parts.append(f"Struggling with: {', '.join(learning['strugglingWith'][:2])}")
        
        if learning['recentBreakthroughs']:
            bt = learning['recentBreakthroughs'][0]
            context_parts.append(f"Recent breakthrough: {bt['topic']}")
        
        # Build final context
        if context_parts:
            context = "CONTEXT FROM PREVIOUS CONVERSATIONS:\n"
            context += "\n".join(f"- {part}" for part in context_parts)
            context += "\n\nUse this context to personalize your response and build on previous discussions.\n\n"
            return context
        
        return ""
    
    def get_conversation_summary(self) -> Dict:
        """
        Get a summary of all conversation history
        
        Returns:
            Dictionary with overall statistics and insights
        """
        all_insights = self.load_recent_insights(limit=50)  # Load up to 50
        
        if not all_insights:
            return {
                'totalConversations': 0,
                'topTopics': [],
                'avgSentiment': 50,
                'totalBreakthroughs': 0
            }
        
        # Aggregate stats
        all_topics = []
        all_sentiments = []
        breakthrough_count = 0
        
        for insight in all_insights:
            all_topics.extend(insight.get('topics', []))
            all_sentiments.append(insight.get('sentimentScore', 50))
            if insight.get('breakthrough'):
                breakthrough_count += 1
        
        # Top topics
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'totalConversations': len(all_insights),
            'topTopics': [{'topic': t, 'count': c} for t, c in top_topics],
            'avgSentiment': round(sum(all_sentiments) / len(all_sentiments)) if all_sentiments else 50,
            'totalBreakthroughs': breakthrough_count,
            'needsAttention': self.needs_attention_check()
        }


def main():
    """Test the context manager"""
    
    cm = ContextManager()
    
    print("="*70)
    print(" Context Manager Test ".center(70))
    print("="*70)
    print()
    
    # Load recent insights
    print("📚 Recent Insights:")
    insights = cm.load_recent_insights(limit=3)
    for i, insight in enumerate(insights, 1):
        print(f"\n{i}. Conversation #{insight.get('conversation_id', 'N/A')}")
        print(f"   Topics: {', '.join(insight.get('topics', []))}")
        print(f"   Emotion: {insight.get('dominantEmotion', 'N/A')}")
        print(f"   Engagement: {insight.get('engagementLevel', 'N/A')}")
        print(f"   Summary: {insight.get('summary', 'N/A')[:80]}...")
    
    print("\n" + "="*70)
    
    # Topic history
    print("\n🎯 Topic History:")
    topics = cm.get_topic_history()
    print(f"   {', '.join(topics) if topics else 'No topics yet'}")
    
    # Emotional trend
    print("\n😊 Emotional Trend:")
    emotional = cm.get_emotional_trend()
    print(f"   Dominant: {emotional['dominantEmotion']}")
    print(f"   Avg Sentiment: {emotional['avgSentiment']}/100")
    print(f"   Trend: {emotional['trend']}")
    
    # Learning context
    print("\n📖 Learning Context:")
    learning = cm.get_learning_context()
    print(f"   High Interest: {', '.join(learning['highInterestTopics']) if learning['highInterestTopics'] else 'None'}")
    print(f"   Struggling: {', '.join(learning['strugglingWith']) if learning['strugglingWith'] else 'None'}")
    print(f"   Breakthroughs: {len(learning['recentBreakthroughs'])}")
    
    # Context for Harry
    print("\n" + "="*70)
    print("\n🧙 Context for Harry:")
    print("="*70)
    context = cm.build_context_for_harry()
    if context:
        print(context)
    else:
        print("No context available yet")
    
    # Summary
    print("\n" + "="*70)
    print("\n📊 Overall Summary:")
    summary = cm.get_conversation_summary()
    print(f"   Total Conversations: {summary['totalConversations']}")
    print(f"   Avg Sentiment: {summary['avgSentiment']}/100")
    print(f"   Breakthroughs: {summary['totalBreakthroughs']}")
    print(f"   Needs Attention: {summary['needsAttention']}")
    print(f"\n   Top Topics:")
    for topic_data in summary['topTopics']:
        print(f"     - {topic_data['topic']} ({topic_data['count']} times)")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

