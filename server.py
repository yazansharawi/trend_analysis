import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LogLevel
)
import mcp.types as types

from config import config
from trend_analyzer import trend_analyzer, TrendData
from sources import get_sources_by_category

# Initialize MCP server
server = Server("trend-analysis-server")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List all available tools"""
    return [
        Tool(
            name="track_trend",
            description="Start tracking a keyword/topic across Twitter and web sources",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "The keyword or phrase to track"
                    },
                    "timeframe": {
                        "type": "string", 
                        "description": "Analysis timeframe (1h, 6h, 24h, 7d)",
                        "default": "24h"
                    }
                },
                "required": ["keyword"]
            }
        ),
        Tool(
            name="analyze_trend",
            description="Get comprehensive trend analysis for a keyword",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "The keyword to analyze"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Analysis timeframe (1h, 6h, 24h, 7d)", 
                        "default": "24h"
                    }
                },
                "required": ["keyword"]
            }
        ),
        Tool(
            name="compare_trends",
            description="Compare sentiment and volume across multiple keywords",
            inputSchema={
                "type": "object", 
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Keywords to compare (max 5)"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Comparison timeframe",
                        "default": "24h"
                    }
                },
                "required": ["keywords"]
            }
        ),
        Tool(
            name="get_trending_topics",
            description="Discover currently trending topics by category",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Category to focus on (tech, finance, general)",
                        "default": "general"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Number of trends to return",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="sentiment_breakdown",
            description="Get detailed sentiment analysis for a keyword",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string", 
                        "description": "Keyword to analyze sentiment for"
                    },
                    "source_type": {
                        "type": "string",
                        "enum": ["twitter", "web", "both"],
                        "description": "Which sources to analyze",
                        "default": "both"
                    }
                },
                "required": ["keyword"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "track_trend":
            return await track_trend(arguments)
        elif name == "analyze_trend":
            return await analyze_trend(arguments)
        elif name == "compare_trends":
            return await compare_trends(arguments)
        elif name == "get_trending_topics":
            return await get_trending_topics(arguments)
        elif name == "sentiment_breakdown":
            return await sentiment_breakdown(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        error_msg = f"Error executing {name}: {str(e)}"
        return [types.TextContent(type="text", text=error_msg)]

async def track_trend(args: Dict[str, Any]) -> List[types.TextContent]:
    """Track a keyword trend"""
    keyword = args.get("keyword")
    timeframe = args.get("timeframe", "24h")
    
    if not keyword:
        return [types.TextContent(type="text", text="Error: keyword is required")]
    
    # Perform trend analysis
    result = trend_analyzer.analyze_trend(keyword, timeframe)
    
    # Format response
    response = {
        "status": "success",
        "message": f"Started tracking '{keyword}'",
        "data": {
            "keyword": result.keyword,
            "timeframe": result.timeframe,
            "total_mentions": result.total_mentions,
            "twitter_mentions": result.twitter_mentions,
            "web_mentions": result.web_mentions,
            "overall_sentiment": result.overall_sentiment["overall_label"],
            "sentiment_score": result.overall_sentiment["overall_score"],
            "trend_direction": result.trend_direction,
            "top_sources": result.top_sources[:3],
            "analysis_time": result.analysis_timestamp
        }
    }
    
    return [types.TextContent(type="text", text=json.dumps(response, indent=2))]

async def analyze_trend(args: Dict[str, Any]) -> List[types.TextContent]:
    """Analyze a keyword trend in detail"""
    keyword = args.get("keyword")
    timeframe = args.get("timeframe", "24h")
    
    if not keyword:
        return [types.TextContent(type="text", text="Error: keyword is required")]
    
    # Perform detailed analysis
    result = trend_analyzer.analyze_trend(keyword, timeframe)
    
    # Create detailed report
    report = f"""# Trend Analysis: {keyword}

## Summary
- **Total Mentions**: {result.total_mentions}
- **Twitter**: {result.twitter_mentions} mentions
- **Web Sources**: {result.web_mentions} mentions
- **Trend Direction**: {result.trend_direction.upper()}

## Sentiment Analysis
### Overall: {result.overall_sentiment['overall_label'].upper()} ({result.overall_sentiment['overall_score']:.3f})
- Positive: {result.overall_sentiment['sentiment_distribution']['positive']}%
- Negative: {result.overall_sentiment['sentiment_distribution']['negative']}%
- Neutral: {result.overall_sentiment['sentiment_distribution']['neutral']}%

### Platform Breakdown:
**Twitter Sentiment**: {result.twitter_sentiment['overall_label']} ({result.twitter_sentiment['overall_score']:.3f})
**Web Sentiment**: {result.web_sentiment['overall_label']} ({result.web_sentiment['overall_score']:.3f})

## Top Sources
{chr(10).join([f"- {source}" for source in result.top_sources[:5]])}

## Sample Mentions
{chr(10).join([f"**{dp.platform.title()}**: {dp.text[:100]}..." for dp in result.sample_mentions[:3]])}

---
*Analysis completed at {result.analysis_timestamp}*
"""
    
    return [types.TextContent(type="text", text=report)]

async def compare_trends(args: Dict[str, Any]) -> List[types.TextContent]:
    """Compare multiple keyword trends"""
    keywords = args.get("keywords", [])
    timeframe = args.get("timeframe", "24h")
    
    if not keywords or len(keywords) == 0:
        return [types.TextContent(type="text", text="Error: keywords list is required")]
    
    if len(keywords) > 5:
        keywords = keywords[:5]  # Limit to 5 for performance
    
    # Analyze each keyword
    results = trend_analyzer.compare_trends(keywords, timeframe)
    
    # Create comparison report
    report = f"# Trend Comparison ({timeframe})\n\n"
    
    # Summary table
    report += "## Summary\n"
    report += "| Keyword | Mentions | Sentiment | Direction |\n"
    report += "|---------|----------|-----------|----------|\n"
    
    for keyword, data in results.items():
        sentiment_label = data.overall_sentiment['overall_label']
        report += f"| {keyword} | {data.total_mentions} | {sentiment_label} | {data.trend_direction} |\n"
    
    # Detailed breakdown
    report += "\n## Detailed Analysis\n"
    for keyword, data in results.items():
        report += f"\n### {keyword}\n"
        report += f"- **Volume**: {data.total_mentions} total ({data.twitter_mentions} Twitter, {data.web_mentions} Web)\n"
        report += f"- **Sentiment**: {data.overall_sentiment['overall_label']} ({data.overall_sentiment['overall_score']:.3f})\n"
        report += f"- **Distribution**: {data.overall_sentiment['sentiment_distribution']['positive']}% positive, "
        report += f"{data.overall_sentiment['sentiment_distribution']['negative']}% negative\n"
    
    return [types.TextContent(type="text", text=report)]

async def get_trending_topics(args: Dict[str, Any]) -> List[types.TextContent]:
    """Get trending topics by category"""
    category = args.get("category", "general")
    limit = args.get("limit", 10)
    
    # Get trending topics
    topics = trend_analyzer.get_trending_topics(category, limit)
    
    response = {
        "category": category,
        "trending_topics": topics,
        "count": len(topics),
        "timestamp": datetime.now().isoformat()
    }
    
    # Format as readable list
    report = f"# Trending Topics: {category.title()}\n\n"
    for i, topic in enumerate(topics, 1):
        report += f"{i}. {topic}\n"
    
    report += f"\n*{len(topics)} topics found*"
    
    return [types.TextContent(type="text", text=report)]

async def sentiment_breakdown(args: Dict[str, Any]) -> List[types.TextContent]:
    """Get detailed sentiment breakdown"""
    keyword = args.get("keyword")
    source_type = args.get("source_type", "both")
    
    if not keyword:
        return [types.TextContent(type="text", text="Error: keyword is required")]
    
    # Analyze the keyword
    result = trend_analyzer.analyze_trend(keyword, "24h")
    
    # Create sentiment report
    report = f"# Sentiment Analysis: {keyword}\n\n"
    
    if source_type in ["both", "twitter"]:
        twitter_sent = result.twitter_sentiment
        report += f"## Twitter Sentiment\n"
        report += f"- **Overall**: {twitter_sent['overall_label']} ({twitter_sent['overall_score']:.3f})\n"
        report += f"- **Mentions**: {twitter_sent['total_count']}\n"
        report += f"- **Distribution**: {twitter_sent['sentiment_distribution']['positive']}% positive, "
        report += f"{twitter_sent['sentiment_distribution']['negative']}% negative, "
        report += f"{twitter_sent['sentiment_distribution']['neutral']}% neutral\n\n"
    
    if source_type in ["both", "web"]:
        web_sent = result.web_sentiment
        report += f"## Web Sentiment\n"
        report += f"- **Overall**: {web_sent['overall_label']} ({web_sent['overall_score']:.3f})\n"
        report += f"- **Mentions**: {web_sent['total_count']}\n"
        report += f"- **Distribution**: {web_sent['sentiment_distribution']['positive']}% positive, "
        report += f"{web_sent['sentiment_distribution']['negative']}% negative, "
        report += f"{web_sent['sentiment_distribution']['neutral']}% neutral\n\n"
    
    if source_type == "both":
        overall = result.overall_sentiment
        report += f"## Combined Sentiment\n"
        report += f"- **Overall**: {overall['overall_label']} ({overall['overall_score']:.3f})\n"
        report += f"- **Total Mentions**: {overall['total_count']}\n"
    
    return [types.TextContent(type="text", text=report)]

async def main():
    """Main server entry point"""
    # Check configuration
    missing_config = config.validate()
    if missing_config:
        print(f"❌ Missing configuration: {', '.join(missing_config)}")
        print("Please check your .env file and ensure all API keys are set")
        return
    
    print("✅ Configuration valid")
    print(f"🚀 Starting Trend Analysis MCP Server v{config.SERVER_VERSION}")
    
    # Import and run MCP server
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=config.SERVER_NAME,
                server_version=config.SERVER_VERSION,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())