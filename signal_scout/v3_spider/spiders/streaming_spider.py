"""
Signal Scout V3 - Streaming Site Spider

This is the main cognitive crawler spider that autonomously discovers and classifies
streaming sites using AI classification and intelligent link following.
"""

import scrapy
import logging
import re
import json
import os
from urllib.parse import urljoin, urlparse
from googlesearch import search
import sys
import time

# Add parent directory to path to import scout modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classifier import StreamingSiteClassifier
from verification import verify_url

logger = logging.getLogger(__name__)


class StreamingSiteSpider(scrapy.Spider):
    """
    V3 Cognitive Crawler Spider for autonomous streaming site discovery.
    
    Features:
    - Genesis Seed Engine: Starts from search queries
    - Focused Crawling: Intelligent link selection with relevancy scoring
    - AI Classification: Real-time page classification
    - Autonomous Feedback Loop: Newly discovered sites become seeds
    """
    
    name = "streaming_spider"
    allowed_domains = []  # Will be populated dynamically
    start_urls = []
    
    # Class-level variables for configuration
    custom_settings = {
        'ROBOTSTXT_OBEY': False,  # Many streaming sites block robots
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 5,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'DEPTH_LIMIT': 3,
        'CLOSESPIDER_PAGECOUNT': 100,  # Limit for testing
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize AI classifier
        self.classifier = StreamingSiteClassifier()
        
        # Initialize Scout instance for verification pipeline
        self.scout_instance = None
        
        # Crawl statistics
        self.stats = {
            'pages_crawled': 0,
            'classified_positive': 0,
            'classified_negative': 0,
            'verified_sites': 0,
            'failed_verifications': 0,
            'new_seeds_added': 0
        }
        
        # Track discovered URLs to avoid duplicates
        self.discovered_urls = set()
        
        # Queue for autonomous feedback loop
        self.feedback_queue = []
        
        logger.info("StreamingSiteSpider initialized with V3 cognitive capabilities")
    
    def _load_config(self):
        """Load configuration from scout_config.json."""
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'scout_config.json')
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info("Configuration loaded successfully")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return {}
    
    def start_requests(self):
        """
        Genesis Seed Engine: Generate initial requests from search queries.
        """
        logger.info("=" * 60)
        logger.info("SIGNAL SCOUT V3 - GENESIS SEED ENGINE ACTIVATED")
        logger.info("=" * 60)
        
        seed_queries = self.config.get('operational_parameters', {}).get('seed_queries', [])
        
        if not seed_queries:
            logger.warning("No seed queries configured, using default")
            seed_queries = ["watch sports online free", "live streaming sites"]
        
        initial_urls = []
        
        for query in seed_queries:
            logger.info(f"Genesis Search: '{query}'")
            try:
                # Use googlesearch to get initial seed URLs
                search_results = list(search(query, num=5, stop=5, pause=2))
                
                for url in search_results:
                    if self._is_valid_seed_url(url):
                        initial_urls.append(url)
                        logger.info(f"Genesis Seed: {url}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Search failed for query '{query}': {e}")
        
        logger.info(f"Genesis Engine generated {len(initial_urls)} seed URLs")
        
        # Create initial requests
        for url in initial_urls:
            if url not in self.discovered_urls:
                self.discovered_urls.add(url)
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={'depth': 0, 'source': 'genesis_seed'},
                    errback=self.handle_error
                )
    
    def _is_valid_seed_url(self, url):
        """Check if URL is valid for seeding."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Skip major search engines and social media
            skip_domains = [
                'google.com', 'bing.com', 'yahoo.com', 'duckduckgo.com',
                'facebook.com', 'twitter.com', 'youtube.com', 'instagram.com',
                'reddit.com', 'wikipedia.org'
            ]
            
            for skip_domain in skip_domains:
                if skip_domain in domain:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def parse(self, response):
        """
        Main parsing method with AI classification and focused crawling.
        """
        url = response.url
        current_depth = response.meta.get('depth', 0)
        source = response.meta.get('source', 'crawl')
        
        self.stats['pages_crawled'] += 1
        
        logger.info(f"V3 Parse: {url} (depth: {current_depth}, source: {source})")
        
        # AI Classification Phase
        classification_result = self.classifier.classify_page(response.text, url)
        
        ai_probability = classification_result.get('probability', 0)
        is_streaming_candidate = classification_result.get('is_streaming_site', False)
        
        logger.info(f"AI Classification: {url} -> {ai_probability:.3f} probability "
                   f"({'POSITIVE' if is_streaming_candidate else 'NEGATIVE'})")
        
        if is_streaming_candidate:
            self.stats['classified_positive'] += 1
        else:
            self.stats['classified_negative'] += 1
        
        # High-confidence streaming sites go to V2 verification pipeline
        ai_threshold = self.config.get('v3_crawler_settings', {}).get('ai_confidence_threshold', 0.7)
        
        if ai_probability >= ai_threshold:
            logger.info(f"V3 -> V2 Verification Pipeline: {url} (confidence: {ai_probability:.3f})")
            self._verify_with_v2_pipeline(url, classification_result)
        
        # Focused Crawling: Extract and score links for continued crawling
        max_depth = self.config.get('v3_crawler_settings', {}).get('max_crawl_depth', 3)
        
        if current_depth < max_depth:
            for next_request in self._extract_focused_links(response, current_depth):
                yield next_request
        
        # Log periodic statistics
        if self.stats['pages_crawled'] % 10 == 0:
            self._log_statistics()
    
    def _verify_with_v2_pipeline(self, url, classification_result):
        """
        Send high-confidence AI classifications to V2 verification pipeline.
        """
        try:
            # Import and use V2 verification
            if not self.scout_instance:
                # Initialize scout instance if needed
                from scout import SignalScout
                self.scout_instance = SignalScout()
            
            # Run V2 verification
            verification_result = verify_url(url, scout_instance=self.scout_instance)
            
            # V2 final verdict using existing threshold
            v2_threshold = self.config.get('discovery_settings', {}).get('verification_confidence_threshold', 50)
            
            if verification_result['overall_confidence'] >= v2_threshold:
                logger.info(f"V3 SUCCESS: {url} passed both AI and V2 verification")
                self.stats['verified_sites'] += 1
                
                # Store in database using V2 system
                self.scout_instance._store_verified_site(url, verification_result)
                
                # Autonomous Feedback Loop: Add to crawl queue
                if self.config.get('v3_crawler_settings', {}).get('enable_autonomous_feedback', True):
                    self._add_to_feedback_queue(url)
                
            else:
                logger.info(f"V3 FILTERED: {url} failed V2 verification (confidence: {verification_result['overall_confidence']})")
                self.stats['failed_verifications'] += 1
                
        except Exception as e:
            logger.error(f"V2 verification failed for {url}: {e}")
            self.stats['failed_verifications'] += 1
    
    def _add_to_feedback_queue(self, url):
        """
        Add successfully verified site to autonomous feedback queue.
        """
        if url not in self.feedback_queue and url not in self.discovered_urls:
            self.feedback_queue.append(url)
            self.stats['new_seeds_added'] += 1
            logger.info(f"Autonomous Feedback: Added {url} to crawl queue")
    
    def _extract_focused_links(self, response, current_depth):
        """
        Intelligent link extraction with relevancy scoring.
        """
        links_found = response.css('a::attr(href)').getall()
        scored_links = []
        
        for link in links_found:
            try:
                # Resolve relative URLs
                full_url = urljoin(response.url, link)
                
                # Skip if already discovered
                if full_url in self.discovered_urls:
                    continue
                
                # Calculate relevancy score
                relevancy_score = self._calculate_relevancy_score(link, full_url)
                
                # Check relevancy threshold
                relevancy_threshold = self.config.get('v3_crawler_settings', {}).get('relevancy_threshold', 0.6)
                
                if relevancy_score >= relevancy_threshold:
                    scored_links.append((full_url, relevancy_score))
                
            except Exception as e:
                logger.debug(f"Error processing link {link}: {e}")
        
        # Sort by relevancy score and limit
        scored_links.sort(key=lambda x: x[1], reverse=True)
        
        max_links = 10  # Limit links per page to maintain focus
        
        for url, score in scored_links[:max_links]:
            if url not in self.discovered_urls:
                self.discovered_urls.add(url)
                
                logger.debug(f"Focused Crawl: {url} (relevancy: {score:.2f})")
                
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={'depth': current_depth + 1, 'source': 'focused_crawl'},
                    errback=self.handle_error
                )
    
    def _calculate_relevancy_score(self, link_text, url):
        """
        Calculate relevancy score for a link based on sports/streaming indicators.
        """
        score = 0.0
        
        # Keyword scoring for anchor text and URL
        streaming_keywords = ['live', 'stream', 'watch', 'tv', 'video', 'player', 'free']
        sports_keywords = ['nfl', 'nba', 'nhl', 'mlb', 'soccer', 'football', 'basketball', 'sports']
        
        text_lower = link_text.lower() if link_text else ""
        url_lower = url.lower()
        
        # Anchor text scoring
        for keyword in streaming_keywords:
            if keyword in text_lower:
                score += 0.3
        
        for keyword in sports_keywords:
            if keyword in text_lower:
                score += 0.2
        
        # URL scoring
        for keyword in streaming_keywords:
            if keyword in url_lower:
                score += 0.2
        
        for keyword in sports_keywords:
            if keyword in url_lower:
                score += 0.15
        
        # Bonus for specific streaming indicators
        if any(indicator in url_lower for indicator in ['live', 'stream', 'watch']):
            score += 0.1
        
        # Penalty for obviously non-streaming links
        negative_indicators = ['privacy', 'terms', 'contact', 'about', 'dmca', 'legal']
        for indicator in negative_indicators:
            if indicator in url_lower or indicator in text_lower:
                score -= 0.5
        
        return max(0.0, min(1.0, score))  # Clamp between 0 and 1
    
    def handle_error(self, failure):
        """Handle request errors."""
        logger.debug(f"Request failed: {failure.request.url} - {failure.value}")
    
    def _log_statistics(self):
        """Log crawl statistics."""
        logger.info("=" * 40)
        logger.info("V3 CRAWLER STATISTICS")
        logger.info(f"Pages Crawled: {self.stats['pages_crawled']}")
        logger.info(f"AI Classifications: +{self.stats['classified_positive']} -{self.stats['classified_negative']}")
        logger.info(f"V2 Verifications: +{self.stats['verified_sites']} -{self.stats['failed_verifications']}")
        logger.info(f"Feedback Queue: {self.stats['new_seeds_added']} new seeds")
        logger.info("=" * 40)
    
    def closed(self, reason):
        """Called when spider closes."""
        logger.info("=" * 60)
        logger.info("SIGNAL SCOUT V3 - SPIDER CLOSING")
        logger.info(f"Reason: {reason}")
        logger.info("FINAL STATISTICS:")
        for key, value in self.stats.items():
            logger.info(f"  {key}: {value}")
        logger.info("=" * 60)
        
        # Clean up scout instance if created
        if self.scout_instance:
            try:
                self.scout_instance._cleanup_browser()
            except Exception as e:
                logger.debug(f"Error cleaning up scout instance: {e}")