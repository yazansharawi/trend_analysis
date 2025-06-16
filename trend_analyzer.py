import tweepy
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
import json
from dataclasses import dataclass, asdict

from config import config
from sentiment import sentiment_analyzer, SentimentResult
from sources import get_sources_for_keyword, DEFAULT_SOURCES

@dataclass
class DataPoint:
    text: str
    source: str 
    url: Optional[str] = None
    timestamp: Optional[str] = None
    engagement: Optional[int] = None  
    platform: str = 'unknown'  

@dataclass 
class TrendData:
    keyword: str
    timeframe: str
    total_mentions: int
    twitter_mentions: int
    web_mentions: int
    overall_sentiment: Dict
    twitter_sentiment: Dict 
    web_sentiment: Dict
    top_sources: List[str]
    sample_mentions: List[DataPoint]
    trend_direction: str  
    analysis_timestamp: str

class TrendAnalyzer:
    
    def __init__(self):
        self.twitter_client = None
        self.firecrawl_api_key = config.FIRECRAWL_API_KEY
        self.cache = {}  
        
        if config.TWITTER_BEARER_TOKEN:
            self.twitter_client = tweepy.Client(
                bearer_token=config.TWITTER_BEARER_TOKEN,
                wait_on_rate_limit=True
            )
    
    def search_twitter(self, keyword: str, max_results: int = 100) -> List[DataPoint]:
        if not self.twitter_client:
            print("Warning: Twitter client not initialized")
            return []
        
        data_points = []
        
        try:
            tweets = tweepy.Paginator(
                self.twitter_client.search_recent_tweets,
                query=f"{keyword} -is:retweet lang:en",
                tweet_fields=['created_at', 'public_metrics', 'context_annotations'],
                max_results=min(max_results, 100),
                limit=1
            ).flatten(limit=max_results)
            
            for tweet in tweets:
                engagement = 0
                if hasattr(tweet, 'public_metrics') and tweet.public_metrics:
                    engagement = (tweet.public_metrics.get('like_count', 0) + 
                                tweet.public_metrics.get('retweet_count', 0))
                
                data_point = DataPoint(
                    text=tweet.text,
                    source='twitter',
                    url=f"https://twitter.com/i/status/{tweet.id}",
                    timestamp=tweet.created_at.isoformat() if tweet.created_at else None,
                    engagement=engagement,
                    platform='twitter'
                )
                data_points.append(data_point)
                
        except Exception as e:
            print(f"Twitter search error: {e}")
        
        return data_points
    
    def search_web(self, keyword: str, sources: Optional[List[str]] = None) -> List[DataPoint]:
        if not self.firecrawl_api_key:
            print("Warning: Firecrawl API key not found")
            return []
        
        if not sources:
            sources = get_sources_for_keyword(keyword)[:5]  
        
        data_points = []
        
        for source_url in sources:
            try:    
                response = requests.post(
                    'https://api.firecrawl.dev/v0/scrape',
                    headers={
                        'Authorization': f'Bearer {self.firecrawl_api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'url': source_url,
                        'formats': ['markdown'],
                        'onlyMainContent': True
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('data', {}).get('markdown'):
                        content = data['data']['markdown']
                        
                        if keyword.lower() in content.lower():
                            sentences = self._extract_keyword_sentences(content, keyword)
                            
                            for sentence in sentences[:3]:  
                                data_point = DataPoint(
                                    text=sentence,
                                    source=source_url,
                                    url=source_url,
                                    timestamp=datetime.now().isoformat(),
                                    platform='web'
                                )
                                data_points.append(data_point)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Error scraping {source_url}: {e}")
                continue
        
        return data_points
    
    def _extract_keyword_sentences(self, content: str, keyword: str, max_sentences: int = 5) -> List[str]:
        sentences = []
        
        text_parts = content.replace('\n', ' ').split('. ')
        
        for part in text_parts:
            if keyword.lower() in part.lower() and len(part.strip()) > 20:
                sentence = part.strip()
                if not sentence.endswith('.'):
                    sentence += '.'
                sentences.append(sentence)
                
                if len(sentences) >= max_sentences:
                    break
        
        return sentences
    
    def analyze_trend(self, keyword: str, timeframe: str = "24h") -> TrendData:
        print(f"Analyzing trend for: {keyword}")
        
        twitter_data = self.search_twitter(keyword, config.MAX_TWEETS_PER_SEARCH)
        web_data = self.search_web(keyword)
        
        print(f"Found {len(twitter_data)} Twitter mentions, {len(web_data)} web mentions")
        
        twitter_texts = [dp.text for dp in twitter_data]
        web_texts = [dp.text for dp in web_data]
        
        twitter_sentiment = sentiment_analyzer.get_overall_sentiment(twitter_texts)
        web_sentiment = sentiment_analyzer.get_overall_sentiment(web_texts)
        
        all_texts = twitter_texts + web_texts
        overall_sentiment = sentiment_analyzer.get_overall_sentiment(all_texts)
        
        trend_direction = self._calculate_trend_direction(twitter_data, web_data)
        
        top_sources = self._get_top_sources(twitter_data + web_data)
        
        sample_mentions = (twitter_data[:3] + web_data[:3])[:6]
        
        return TrendData(
            keyword=keyword,
            timeframe=timeframe,
            total_mentions=len(twitter_data) + len(web_data),
            twitter_mentions=len(twitter_data),
            web_mentions=len(web_data),
            overall_sentiment=overall_sentiment,
            twitter_sentiment=twitter_sentiment,
            web_sentiment=web_sentiment,
            top_sources=top_sources,
            sample_mentions=sample_mentions,
            trend_direction=trend_direction,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def _calculate_trend_direction(self, twitter_data: List[DataPoint], web_data: List[DataPoint]) -> str:  
        total_volume = len(twitter_data) + len(web_data)
        
        if total_volume > 50:
            return 'rising'
        elif total_volume > 10:
            return 'stable'
        else:
            return 'falling'
    
    def _get_top_sources(self, data_points: List[DataPoint]) -> List[str]:
        source_counts = {}
        
        for dp in data_points:
            source = dp.source
            source_counts[source] = source_counts.get(source, 0) + 1
        
        sorted_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
        return [source for source, count in sorted_sources[:5]]
    
    def compare_trends(self, keywords: List[str], timeframe: str = "24h") -> Dict[str, TrendData]:
        results = {}
        
        for keyword in keywords:
            try:
                results[keyword] = self.analyze_trend(keyword, timeframe)
                time.sleep(2)  
            except Exception as e:
                print(f"Error analyzing {keyword}: {e}")
                continue
        
        return results
    
    def get_trending_topics(self, category: str = "general", limit: int = 10) -> List[str]:
        trending_topics = {
            "tech": ["AI", "ChatGPT", "Tesla", "Apple", "Google", "Microsoft", "OpenAI", "Blockchain"],
            "general": ["Climate change", "Economy", "Politics", "Sports", "Entertainment", "Health", "Education"],
            "finance": ["Bitcoin", "Stock market", "Fed rates", "Inflation", "Tesla stock", "AI stocks"]
        }
        
        topics = trending_topics.get(category, trending_topics["general"])
        return topics[:limit]

trend_analyzer = TrendAnalyzer()

if __name__ == "__main__":
    analyzer = TrendAnalyzer()
    
    result = analyzer.analyze_trend("AI regulation")
    print(f"Analysis complete for 'AI regulation':")
    print(f"- Total mentions: {result.total_mentions}")
    print(f"- Overall sentiment: {result.overall_sentiment['overall_label']}")
    print(f"- Trend direction: {result.trend_direction}")