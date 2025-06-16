TECH_SOURCES = [
    "https://techcrunch.com",
    "https://www.theverge.com", 
    "https://arstechnica.com",
    "https://www.wired.com",
    "https://venturebeat.com",
    "https://www.businessinsider.com/tech",
]

# General News Sources
NEWS_SOURCES = [
    "https://www.reuters.com",
    "https://www.bbc.com/news",
    "https://www.cnn.com",
    "https://www.npr.org",
    "https://apnews.com",
]

# Discussion and Community Sources
DISCUSSION_SOURCES = [
    "https://news.ycombinator.com",
    "https://www.reddit.com/r/technology",
    "https://www.reddit.com/r/worldnews", 
    "https://medium.com",
    "https://dev.to",
]

# Financial and Market Sources
FINANCE_SOURCES = [
    "https://www.bloomberg.com",
    "https://finance.yahoo.com",
    "https://www.marketwatch.com",
    "https://www.cnbc.com",
    "https://www.fool.com",
]

# Social Media and Culture
CULTURE_SOURCES = [
    "https://www.buzzfeednews.com",
    "https://mashable.com",
    "https://gizmodo.com",
    "https://lifehacker.com",
]

# All sources combined for general trending
ALL_SOURCES = TECH_SOURCES + NEWS_SOURCES + DISCUSSION_SOURCES + FINANCE_SOURCES + CULTURE_SOURCES

# Category mapping for targeted analysis
SOURCE_CATEGORIES = {
    "tech": TECH_SOURCES,
    "news": NEWS_SOURCES,
    "discussion": DISCUSSION_SOURCES,
    "finance": FINANCE_SOURCES,
    "culture": CULTURE_SOURCES,
    "all": ALL_SOURCES,
}

def get_sources_by_category(category: str = "all") -> list:
    """
    Get web sources by category
    
    Args:
        category: One of 'tech', 'news', 'discussion', 'finance', 'culture', 'all'
        
    Returns:
        List of URLs for the specified category
    """
    return SOURCE_CATEGORIES.get(category.lower(), ALL_SOURCES)

def get_sources_for_keyword(keyword: str) -> list:
    """
    Get relevant sources based on keyword analysis
    
    Args:
        keyword: The keyword/topic being analyzed
        
    Returns:
        List of most relevant URLs for the keyword
    """
    keyword_lower = keyword.lower()
    
    # Tech-related keywords
    tech_keywords = ['ai', 'artificial intelligence', 'machine learning', 'crypto', 'bitcoin', 
                    'blockchain', 'startup', 'tech', 'software', 'app', 'saas', 'api',
                    'programming', 'coding', 'developer', 'github', 'open source']
    
    # Finance-related keywords  
    finance_keywords = ['stock', 'market', 'trading', 'investment', 'economy', 'inflation',
                       'fed', 'interest rate', 'earnings', 'ipo', 'revenue', 'profit']
    
    # News-related keywords
    news_keywords = ['politics', 'election', 'government', 'policy', 'law', 'court',
                    'climate', 'health', 'covid', 'war', 'international']
    
    # Determine best sources based on keyword
    if any(kw in keyword_lower for kw in tech_keywords):
        return TECH_SOURCES + DISCUSSION_SOURCES[:2]  # Tech + HN + Reddit tech
    elif any(kw in keyword_lower for kw in finance_keywords):
        return FINANCE_SOURCES + NEWS_SOURCES[:3]  # Finance + top news
    elif any(kw in keyword_lower for kw in news_keywords):
        return NEWS_SOURCES + DISCUSSION_SOURCES[:1]  # News + HN
    else:
        # General keyword - use mix of all categories
        return (TECH_SOURCES[:2] + NEWS_SOURCES[:3] + 
                DISCUSSION_SOURCES[:2] + FINANCE_SOURCES[:1])

# Quick access to most reliable sources for MVP
DEFAULT_SOURCES = [
    "https://news.ycombinator.com",  # Great for tech trends
    "https://techcrunch.com",        # Tech news
    "https://www.reuters.com",       # Reliable news
    "https://www.reddit.com/r/technology",  # Community discussions
    "https://www.bloomberg.com",     # Business/finance
]

if __name__ == "__main__":
    # Test the functions
    print("Tech sources:", len(get_sources_by_category("tech")))
    print("Sources for 'AI regulation':", get_sources_for_keyword("AI regulation"))
    print("Default sources:", DEFAULT_SOURCES)