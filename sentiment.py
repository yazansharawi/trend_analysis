from textblob import TextBlob
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class SentimentResult:
    """Sentiment analysis result"""
    text: str
    score: float  # -1 (negative) to 1 (positive)
    confidence: float  # 0 to 1
    label: str  # 'positive', 'negative', 'neutral'
    
class SentimentAnalyzer:
    """Simple sentiment analyzer using TextBlob"""
    
    def __init__(self):
        # Thresholds for sentiment classification
        self.positive_threshold = 0.1
        self.negative_threshold = -0.1
        
        # Common words that might skew sentiment in trend analysis
        self.noise_words = {
            'trend', 'trending', 'viral', 'popular', 'hot', 'breaking',
            'update', 'news', 'report', 'analysis', 'data', 'chart'
        }
    
    def clean_text(self, text: str) -> str:
        """Clean text for better sentiment analysis"""
        if not text:
            return ""
            
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove mentions and hashtags for cleaner analysis
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def analyze_text(self, text: str) -> SentimentResult:
        """Analyze sentiment of a single text"""
        if not text or not text.strip():
            return SentimentResult(
                text=text,
                score=0.0,
                confidence=0.0,
                label='neutral'
            )
        
        # Clean the text
        cleaned_text = self.clean_text(text)
        
        # Use TextBlob for sentiment analysis
        blob = TextBlob(cleaned_text)
        
        # Get polarity score (-1 to 1)
        polarity = blob.sentiment.polarity
        
        # Get subjectivity (0 to 1) - use as confidence measure
        subjectivity = blob.sentiment.subjectivity
        
        # Classify sentiment
        if polarity > self.positive_threshold:
            label = 'positive'
        elif polarity < self.negative_threshold:
            label = 'negative'
        else:
            label = 'neutral'
        
        return SentimentResult(
            text=text,
            score=polarity,
            confidence=subjectivity,
            label=label
        )
    
    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """Analyze sentiment for multiple texts"""
        return [self.analyze_text(text) for text in texts]
    
    def get_overall_sentiment(self, texts: List[str]) -> Dict:
        """Get aggregated sentiment for a list of texts"""
        if not texts:
            return {
                'overall_score': 0.0,
                'overall_label': 'neutral',
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_count': 0,
                'confidence': 0.0
            }
        
        results = self.analyze_batch(texts)
        
        # Calculate aggregated metrics
        positive_count = sum(1 for r in results if r.label == 'positive')
        negative_count = sum(1 for r in results if r.label == 'negative')
        neutral_count = sum(1 for r in results if r.label == 'neutral')
        
        # Average sentiment score
        avg_score = sum(r.score for r in results) / len(results)
        
        # Average confidence
        avg_confidence = sum(r.confidence for r in results) / len(results)
        
        # Overall label based on average score
        if avg_score > self.positive_threshold:
            overall_label = 'positive'
        elif avg_score < self.negative_threshold:
            overall_label = 'negative'
        else:
            overall_label = 'neutral'
        
        return {
            'overall_score': round(avg_score, 3),
            'overall_label': overall_label,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_count': len(results),
            'confidence': round(avg_confidence, 3),
            'sentiment_distribution': {
                'positive': round(positive_count / len(results) * 100, 1),
                'negative': round(negative_count / len(results) * 100, 1),
                'neutral': round(neutral_count / len(results) * 100, 1)
            }
        }
    
    def compare_sentiments(self, datasets: Dict[str, List[str]]) -> Dict:
        """Compare sentiment across multiple datasets (e.g., Twitter vs Web)"""
        comparison = {}
        
        for name, texts in datasets.items():
            comparison[name] = self.get_overall_sentiment(texts)
        
        return comparison

def quick_sentiment(text: str) -> float:
    """Quick sentiment score for a single text (-1 to 1)"""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze_text(text)
    return result.score

def batch_sentiment(texts: List[str]) -> float:
    """Quick average sentiment for multiple texts"""
    analyzer = SentimentAnalyzer()
    overall = analyzer.get_overall_sentiment(texts)
    return overall['overall_score']

# Create global analyzer instance for reuse
sentiment_analyzer = SentimentAnalyzer()

if __name__ == "__main__":
    # Test the sentiment analyzer
    test_texts = [
        "I love this new AI technology!",
        "This is terrible and broken",
        "The weather is okay today",
        "Amazing breakthrough in quantum computing!",
        "Disappointed with the latest update"
    ]
    
    analyzer = SentimentAnalyzer()
    
    # Test individual analysis
    for text in test_texts:
        result = analyzer.analyze_text(text)
        print(f"'{text}' -> {result.label} ({result.score:.3f})")
    
    # Test overall sentiment
    overall = analyzer.get_overall_sentiment(test_texts)
    print(f"\nOverall: {overall['overall_label']} ({overall['overall_score']})")
    print(f"Distribution: {overall['sentiment_distribution']}")