# Trend Analysis MCP Server

A Model Context Protocol (MCP) server that combines Twitter and web data to provide comprehensive trend analysis and sentiment monitoring. Perfect for market research, brand monitoring, and understanding public opinion across multiple platforms.

## 🚀 Features

- **📊 Multi-Platform Analysis**: Combines Twitter tweets with web content from news sites, blogs, and forums
- **😊 Sentiment Analysis**: Real-time sentiment scoring using TextBlob
- **📈 Trend Direction**: Identifies if topics are rising, falling, or stable
- **⚖️ Comparison Tools**: Compare multiple keywords/topics side-by-side
- **🎯 Smart Source Selection**: Automatically picks relevant websites based on keywords
- **🔄 Real-time Data**: Fresh data from Twitter API v2 and web scraping via Firecrawl

## 🛠 Installation

### Prerequisites
- Python 3.8+
- Twitter Developer Account
- Firecrawl API Account

### 1. Clone & Install
```bash
git clone <your-repo-url>
cd trend-analysis-mcp
pip install -r requirements.txt
```

### 2. Get API Keys

#### Twitter API
1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Apply for developer access (use this description):
   > "Trend analysis application that combines Twitter data with web content for market intelligence and sentiment monitoring. Collects public tweets with specific keywords to analyze sentiment, track trending topics, and generate business insights. No personal data storage beyond aggregated analytics."
3. Create a new app and get your credentials from "Keys and tokens" tab

#### Firecrawl API  
1. Go to [Firecrawl.dev](https://firecrawl.dev)
2. Sign up and get your API key from the dashboard

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

Your `.env` should look like:
```env
TWITTER_BEARER_TOKEN=your_actual_bearer_token
TWITTER_API_KEY=your_actual_api_key
TWITTER_API_SECRET=your_actual_api_secret
TWITTER_ACCESS_TOKEN=your_actual_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_actual_access_token_secret
FIRECRAWL_API_KEY=your_actual_firecrawl_key
```

### 4. Test Installation
```bash
python server.py
```
You should see: ✅ Configuration valid

## 🔧 MCP Configuration

Add this to your Claude Desktop configuration file:

**On macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**On Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "trend-analysis": {
      "command": "python",
      "args": ["/path/to/your/trend-analysis-mcp/server.py"],
      "env": {
        "TWITTER_BEARER_TOKEN": "your_bearer_token",
        "FIRECRAWL_API_KEY": "your_firecrawl_key"
      }
    }
  }
}
```

## 📖 Usage

Once connected to Claude, you can use these commands:

### Track a Trend
```
Track sentiment for "AI regulation" over the last 24 hours
```

### Compare Topics
```
Compare trends between "ChatGPT", "Claude AI", and "Gemini" 
```

### Get Trending Topics
```
What's trending in tech right now?
```

### Detailed Analysis
```
Give me a detailed sentiment breakdown for "Bitcoin" from both Twitter and web sources
```

### Custom Timeframes
```
Analyze "climate change" sentiment over the past week
```

## 🛠 Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `track_trend` | Track keyword across platforms | `keyword`, `timeframe` |
| `analyze_trend` | Detailed trend analysis | `keyword`, `timeframe` |
| `compare_trends` | Compare multiple keywords | `keywords[]`, `timeframe` |
| `get_trending_topics` | Discover trending topics | `category`, `limit` |
| `sentiment_breakdown` | Platform-specific sentiment | `keyword`, `source_type` |

## 📊 Example Output

```markdown
# Trend Analysis: AI regulation

## Summary
- **Total Mentions**: 156
- **Twitter**: 89 mentions  
- **Web Sources**: 67 mentions
- **Trend Direction**: RISING

## Sentiment Analysis
### Overall: NEGATIVE (-0.234)
- Positive: 23.1%
- Negative: 51.3% 
- Neutral: 25.6%

### Platform Breakdown:
**Twitter Sentiment**: negative (-0.312)
**Web Sentiment**: neutral (-0.089)

## Top Sources
- twitter
- techcrunch.com
- reuters.com
- news.ycombinator.com
```

## ⚙️ Configuration Options

You can customize behavior in your `.env`:

```env
MAX_TWEETS_PER_SEARCH=100        # Tweets to fetch per search
MAX_WEB_SOURCES=10               # Web sources to scrape
DEFAULT_TIMEFRAME=24h            # Default analysis window  
CACHE_DURATION_MINUTES=30        # Cache duration
DEBUG=false                      # Enable debug logging
```

## 🔍 Troubleshooting

### Common Issues

**"Missing required configuration"**
- Check your `.env` file has all required API keys
- Verify API keys are valid by testing them directly

**"Twitter API error"**
- Check your Twitter API access level (Free vs Basic)
- Verify rate limits haven't been exceeded
- Ensure Bearer Token is correct

**"Firecrawl API error"**  
- Verify your Firecrawl API key
- Check if you've exceeded your plan limits
- Some websites may block scraping

**"No mentions found"**
- Try different keywords or broader terms
- Check if the topic is actually being discussed
- Verify your search timeframe isn't too narrow

### Rate Limits

- **Twitter Free**: 500K tweets/month
- **Twitter Basic**: 10M tweets/month ($100/month)
- **Firecrawl**: Varies by plan

## 🚀 Next Steps

This is an MVP! Here's what you could add:

### Short Term
- [ ] **Database storage** for historical data
- [ ] **Caching layer** (Redis) for better performance  
- [ ] **Better sentiment models** (Hugging Face Transformers)
- [ ] **Visualization tools** for trend charts

### Medium Term
- [ ] **Real-time streaming** from Twitter
- [ ] **More data sources** (Reddit, LinkedIn, YouTube)
- [ ] **Advanced analytics** (correlation analysis, forecasting)
- [ ] **API rate limiting** and queue management

### Long Term
- [ ] **Machine learning** for trend prediction
- [ ] **Custom alerts** and notifications
- [ ] **Dashboard interface** for non-technical users
- [ ] **Enterprise features** (team management, reporting)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Create an issue for bugs or feature requests
- Check existing issues before creating new ones
- Provide logs and configuration details when reporting issues

## 🙏 Acknowledgments

- [MCP SDK](https://github.com/modelcontextprotocol/python-sdk) for the protocol implementation
- [Tweepy](https://www.tweepy.org/) for Twitter API integration
- [Firecrawl](https://firecrawl.dev) for web scraping capabilities
- [TextBlob](https://textblob.readthedocs.io/) for sentiment analysis

---

**Happy trending! 📈**