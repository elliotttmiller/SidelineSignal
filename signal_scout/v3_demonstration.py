#!/usr/bin/env python3
"""
Signal Scout V3 Demonstration Script

This script demonstrates the V3 Cognitive Crawler capabilities including:
- AI Classification Engine
- Genesis Seed Engine  
- Focused Crawling Logic
- Autonomous Feedback Loop
"""

import logging
import sys
import os

# Configure logging for demo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - V3 DEMO - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def demo_ai_classifier():
    """Demonstrate the AI classification capabilities."""
    logger.info("=" * 60)
    logger.info("DEMO 1: AI CLASSIFICATION ENGINE")
    logger.info("=" * 60)
    
    try:
        from classifier import StreamingSiteClassifier
        
        classifier = StreamingSiteClassifier()
        
        # Test cases: positive and negative examples
        test_cases = [
            {
                'name': 'Streaming Site (Positive)',
                'html': '''
                <html>
                    <head><title>Live Sports Streaming - Watch NFL Free</title></head>
                    <body>
                        <h1>Watch Live Sports Online</h1>
                        <div>Stream NFL, NBA, MLB games for free</div>
                        <video controls>
                            <source src="stream.m3u8" type="application/x-mpegURL">
                        </video>
                        <iframe src="player.html"></iframe>
                        <script src="jwplayer.js"></script>
                    </body>
                </html>
                ''',
                'url': 'https://streameast.live'
            },
            {
                'name': 'News Site (Negative)',
                'html': '''
                <html>
                    <head><title>CNN - Breaking News</title></head>
                    <body>
                        <h1>Latest News</h1>
                        <div>Read the latest news articles</div>
                        <p>Politics, world news, and more</p>
                    </body>
                </html>
                ''',
                'url': 'https://cnn.com'
            }
        ]
        
        for test_case in test_cases:
            logger.info(f"\nTesting: {test_case['name']}")
            logger.info(f"URL: {test_case['url']}")
            
            result = classifier.classify_page(test_case['html'], test_case['url'])
            
            logger.info(f"AI Verdict: {'STREAMING SITE' if result['is_streaming_site'] else 'NOT STREAMING'}")
            logger.info(f"Confidence: {result['probability']:.3f} ({result['confidence']})")
            logger.info(f"Key Features: {result['key_features']}")
        
        logger.info("\n✓ AI Classification Engine demonstrated successfully")
        return True
        
    except Exception as e:
        logger.error(f"AI Classification demo failed: {e}")
        return False

def demo_genesis_seed_engine():
    """Demonstrate the Genesis Seed Engine."""
    logger.info("=" * 60)
    logger.info("DEMO 2: GENESIS SEED ENGINE")
    logger.info("=" * 60)
    
    try:
        # Load configuration
        import json
        config_path = os.path.join(os.path.dirname(__file__), 'scout_config.json')
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        seed_queries = config.get('operational_parameters', {}).get('seed_queries', [])
        
        logger.info("Configured seed queries for autonomous discovery:")
        for i, query in enumerate(seed_queries, 1):
            logger.info(f"  {i}. '{query}'")
        
        logger.info(f"\nGenesis Engine will search for {len(seed_queries)} different queries")
        logger.info("Each query generates 5 initial seed URLs for crawling")
        logger.info("Seeds are filtered to exclude major platforms (Google, Facebook, etc.)")
        
        logger.info("\n✓ Genesis Seed Engine configuration demonstrated")
        return True
        
    except Exception as e:
        logger.error(f"Genesis Seed Engine demo failed: {e}")
        return False

def demo_focused_crawling():
    """Demonstrate focused crawling logic."""
    logger.info("=" * 60)
    logger.info("DEMO 3: FOCUSED CRAWLING LOGIC")
    logger.info("=" * 60)
    
    try:
        # Simulate relevancy scoring
        sample_links = [
            ("Watch live sports", "https://example.com/live-sports"),
            ("Contact us", "https://example.com/contact"),
            ("NFL streaming free", "https://stream.example.com/nfl"),
            ("Privacy policy", "https://example.com/privacy"),
            ("Basketball live stream", "https://example.com/basketball-live")
        ]
        
        logger.info("Relevancy scoring for sample links:")
        
        for link_text, url in sample_links:
            # Simplified scoring logic for demo
            score = 0.0
            
            # Streaming keywords
            streaming_keywords = ['live', 'stream', 'watch', 'tv', 'video']
            for kw in streaming_keywords:
                if kw in link_text.lower():
                    score += 0.3
                if kw in url.lower():
                    score += 0.2
            
            # Sports keywords  
            sports_keywords = ['nfl', 'nba', 'basketball', 'sports']
            for kw in sports_keywords:
                if kw in link_text.lower():
                    score += 0.2
                if kw in url.lower():
                    score += 0.15
            
            # Negative indicators
            negative = ['contact', 'privacy', 'terms', 'about']
            for neg in negative:
                if neg in link_text.lower() or neg in url.lower():
                    score -= 0.5
            
            score = max(0.0, min(1.0, score))
            
            status = "✓ FOLLOW" if score >= 0.6 else "✗ SKIP"
            logger.info(f"  {status} | Score: {score:.2f} | {link_text} -> {url}")
        
        logger.info(f"\nCrawling threshold: 0.6 (configurable)")
        logger.info("Only links above threshold are followed to maintain focus")
        
        logger.info("\n✓ Focused Crawling Logic demonstrated")
        return True
        
    except Exception as e:
        logger.error(f"Focused Crawling demo failed: {e}")
        return False

def demo_v3_integration():
    """Demonstrate V3 integration with V2 system."""
    logger.info("=" * 60)
    logger.info("DEMO 4: V3 INTEGRATION WITH V2 PIPELINE")
    logger.info("=" * 60)
    
    try:
        from v3_integration import check_v3_dependencies
        
        # Check dependencies
        deps_available = check_v3_dependencies()
        
        logger.info("V3 System Status:")
        logger.info(f"  Dependencies: {'✓ Available' if deps_available else '✗ Missing'}")
        logger.info(f"  AI Model: {'✓ Trained' if os.path.exists('scout_model.pkl') else '✗ Not found'}")
        logger.info(f"  Scrapy Spider: {'✓ Ready' if os.path.exists('v3_spider/spiders/streaming_spider.py') else '✗ Missing'}")
        
        logger.info("\nAvailable operation modes:")
        logger.info("  • v2      - Traditional V2 hunter-based discovery")
        logger.info("  • v3      - Pure V3 autonomous cognitive crawling")  
        logger.info("  • hybrid  - Combined V2 + V3 for maximum coverage")
        
        logger.info("\nV3 Autonomous Process:")
        logger.info("  1. Genesis Seed Engine performs search queries")
        logger.info("  2. Spider crawls discovered URLs with focused logic")
        logger.info("  3. AI Classifier evaluates each page in real-time")
        logger.info("  4. High-confidence sites go to V2 verification pipeline")
        logger.info("  5. Verified sites added to database AND crawl queue")
        logger.info("  6. Autonomous feedback loop creates exponential discovery")
        
        logger.info("\n✓ V3 Integration demonstrated")
        return True
        
    except Exception as e:
        logger.error(f"V3 Integration demo failed: {e}")
        return False

def main():
    """Run the complete V3 demonstration."""
    logger.info("🚀 SIGNAL SCOUT V3 COGNITIVE CRAWLER DEMONSTRATION")
    logger.info("🤖 Evolution from V2 (Verifier) to V3 (Autonomous Discoverer)")
    logger.info("")
    
    demos = [
        ("AI Classification Engine", demo_ai_classifier),
        ("Genesis Seed Engine", demo_genesis_seed_engine), 
        ("Focused Crawling Logic", demo_focused_crawling),
        ("V3 Integration", demo_v3_integration)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        try:
            success = demo_func()
            results.append((demo_name, success))
        except Exception as e:
            logger.error(f"Demo '{demo_name}' failed: {e}")
            results.append((demo_name, False))
    
    # Summary
    logger.info("=" * 60)
    logger.info("DEMONSTRATION SUMMARY")
    logger.info("=" * 60)
    
    for demo_name, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"{status} | {demo_name}")
    
    successful_demos = sum(1 for _, success in results if success)
    total_demos = len(results)
    
    logger.info("")
    logger.info(f"Demo Results: {successful_demos}/{total_demos} successful")
    
    if successful_demos == total_demos:
        logger.info("🎉 Signal Scout V3 Cognitive Crawler is fully operational!")
        logger.info("🔥 Ready for autonomous streaming site discovery at scale")
    else:
        logger.info("⚠️  Some V3 components need attention")
    
    return successful_demos == total_demos

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)