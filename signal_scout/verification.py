"""
Verification pipeline for validating discovered streaming sites.
This module implements a multi-stage verification process to ensure site quality.
"""

import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse
import re
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def probe_reachability(url, timeout=10):
    """
    Probe: Simple reachability test to ensure the site responds.
    
    Args:
        url (str): URL to test
        timeout (int): Request timeout in seconds
        
    Returns:
        dict: Result with success status and metadata
    """
    logger.debug(f"Probing reachability for {url}")
    
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        
        result = {
            'success': 200 <= response.status_code < 400,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'final_url': response.url,
            'error': None
        }
        
        if result['success']:
            logger.debug(f"Probe SUCCESS: {url} -> {response.status_code}")
        else:
            logger.debug(f"Probe FAILED: {url} -> {response.status_code}")
            
        return result
        
    except requests.RequestException as e:
        logger.debug(f"Probe ERROR: {url} -> {str(e)}")
        return {
            'success': False,
            'status_code': 0,
            'response_time': timeout,
            'final_url': url,
            'error': str(e)
        }


def analyze_content(url, timeout=10, scout_instance=None):
    """
    V2 Content Analysis: Examines page title and meta content for streaming indicators using dynamic content.
    
    Args:
        url (str): URL to analyze
        timeout (int): Request timeout in seconds
        scout_instance: SignalScout instance for browser access
        
    Returns:
        dict: Analysis result with confidence score and indicators
    """
    logger.debug(f"Analyzing content for {url}")
    
    # V2: Try to use dynamic content first
    if scout_instance and hasattr(scout_instance, 'get_dynamic_page_content'):
        dynamic_result = scout_instance.get_dynamic_page_content(url, timeout)
        if dynamic_result and dynamic_result['success']:
            return _analyze_content_from_html(dynamic_result['content'], dynamic_result['title'])
    
    # Fallback to traditional requests method
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        
        if response.status_code >= 400:
            return {
                'success': False,
                'confidence_score': 0,
                'indicators': [],
                'title': None,
                'error': f'HTTP {response.status_code}'
            }
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_element = soup.find('title')
        title = title_element.text.strip() if title_element else ''
        
        return _analyze_content_from_html(response.text, title)
        
    except Exception as e:
        logger.debug(f"Content analysis ERROR: {url} -> {str(e)}")
        return {
            'success': False,
            'confidence_score': 0,
            'indicators': [],
            'title': None,
            'error': str(e)
        }


def _analyze_content_from_html(html_content, title):
    """
    Helper function to analyze HTML content for streaming indicators.
    
    Args:
        html_content (str): HTML content to analyze
        title (str): Page title
        
    Returns:
        dict: Analysis result
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ''
        
        # Combine text for analysis
        content_text = f"{title} {description}".lower()
        
        # V2: Enhanced streaming indicators with weighted scoring
        indicators = []
        confidence_score = 10  # V2: Base score of 10
        
        streaming_keywords = {
            'stream': 25,      # Increased weights for V2
            'watch': 25,
            'live': 20,
            'movie': 20,
            'tv': 20,
            'sport': 20,
            'free': 15,
            'online': 15,
            'hd': 10,
            'video': 15,
            'player': 15,
            'schedule': 20,
            'games': 15,
            'nfl': 15,
            'nba': 15,
            'soccer': 15,
            'football': 15,
            'nhl': 15,
            'mlb': 15,
            'ufc': 15,
            'boxing': 15,
            'tennis': 15,
            'basketball': 15
        }
        
        for keyword, weight in streaming_keywords.items():
            if keyword in content_text:
                indicators.append(f"keyword_{keyword}")
                confidence_score += weight
        
        # V2: Enhanced bonus system
        if len(indicators) > 3:
            confidence_score += 15  # Bonus for multiple indicators
        if len(indicators) > 6:
            confidence_score += 10  # Additional bonus for many indicators
            
        # V2: Look for specific streaming patterns in content
        streaming_patterns = [
            r'live\s+stream', r'watch\s+online', r'free\s+stream',
            r'hd\s+quality', r'no\s+ads', r'schedule', r'fixtures'
        ]
        
        for pattern in streaming_patterns:
            if re.search(pattern, content_text, re.IGNORECASE):
                indicators.append(f"pattern_{pattern.replace('\\s+', '_')}")
                confidence_score += 10
        
        result = {
            'success': True,
            'confidence_score': confidence_score,
            'indicators': indicators,
            'title': title,
            'error': None
        }
        
        logger.debug(f"Content analysis completed: score={confidence_score}, indicators={len(indicators)}")
        return result
        
    except Exception as e:
        logger.debug(f"Content analysis ERROR: {str(e)}")
        return {
            'success': False,
            'confidence_score': 0,
            'indicators': [],
            'title': None,
            'error': str(e)
        }


def fingerprint_dom(url, timeout=10, scout_instance=None):
    """
    V2 DOM Fingerprinting: The most critical test that examines HTML structure for streaming indicators using dynamic content.
    
    Args:
        url (str): URL to fingerprint
        timeout (int): Request timeout in seconds
        scout_instance: SignalScout instance for browser access
        
    Returns:
        dict: Fingerprinting result with structural indicators
    """
    logger.debug(f"DOM fingerprinting for {url}")
    
    # V2: Try to use dynamic content first
    if scout_instance and hasattr(scout_instance, 'get_dynamic_page_content'):
        dynamic_result = scout_instance.get_dynamic_page_content(url, timeout)
        if dynamic_result and dynamic_result['success']:
            return _fingerprint_dom_from_html(dynamic_result['content'])
    
    # Fallback to traditional requests method
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        
        if response.status_code >= 400:
            return {
                'success': False,
                'confidence_score': 0,
                'structural_indicators': [],
                'error': f'HTTP {response.status_code}'
            }
        
        return _fingerprint_dom_from_html(response.text)
        
    except Exception as e:
        logger.debug(f"DOM fingerprinting ERROR: {url} -> {str(e)}")
        return {
            'success': False,
            'confidence_score': 0,
            'structural_indicators': [],
            'error': str(e)
        }


def _fingerprint_dom_from_html(html_content):
    """
    Helper function to fingerprint DOM structure from HTML content.
    
    Args:
        html_content (str): HTML content to analyze
        
    Returns:
        dict: Fingerprinting result
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        structural_indicators = []
        confidence_score = 0  # V2: Start at 0, will add base score in main function
        
        # V2: Enhanced video detection with higher weights
        video_tags = soup.find_all('video')
        if video_tags:
            structural_indicators.append(f"video_tags_{len(video_tags)}")
            confidence_score += 40  # V2: Increased from 30 to 40
        
        # Look for iframe elements (common in streaming sites)
        iframes = soup.find_all('iframe')
        if iframes:
            structural_indicators.append(f"iframes_{len(iframes)}")
            confidence_score += 35  # V2: Increased from 25 to 35
            
            # Check iframe sources for streaming indicators
            for iframe in iframes:
                src = iframe.get('src', '').lower()
                if any(keyword in src for keyword in ['player', 'stream', 'video', 'embed', 'jwplayer']):
                    structural_indicators.append("streaming_iframe")
                    confidence_score += 25  # V2: Increased from 15 to 25
                    break
        
        # V2: Enhanced streaming selectors with more patterns
        streaming_selectors = [
            # IDs
            {'id': 'player'}, {'id': 'video-player'}, {'id': 'stream'}, {'id': 'live-stream'},
            {'id': 'schedule'}, {'id': 'games'}, {'id': 'matches'}, {'id': 'fixtures'},
            {'id': 'video-container'}, {'id': 'player-container'},
            # Classes
            {'class': 'player'}, {'class': 'video-player'}, {'class': 'stream'},
            {'class': 'live-stream'}, {'class': 'schedule'}, {'class': 'games'}, 
            {'class': 'matches'}, {'class': 'fixtures'}, {'class': 'video-container'}
        ]
        
        for selector in streaming_selectors:
            elements = soup.find_all('div', selector)
            if elements:
                key = list(selector.keys())[0]
                value = list(selector.values())[0]
                structural_indicators.append(f"{key}_{value}")
                confidence_score += 15  # V2: Increased from 10 to 15
        
        # V2: Enhanced script analysis for streaming indicators
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                script_content = script.string.lower()
                streaming_script_patterns = [
                    'player', 'video', 'stream', 'jwplayer', 'hls',
                    'videojs', 'flowplayer', 'plyr', 'm3u8'
                ]
                
                for pattern in streaming_script_patterns:
                    if pattern in script_content:
                        structural_indicators.append(f"streaming_script_{pattern}")
                        confidence_score += 20  # V2: Increased from 15 to 20
                        break
        
        # V2: Enhanced pattern detection for streaming sites
        if soup.find('div', {'class': re.compile(r'.*schedule.*', re.I)}):
            structural_indicators.append("schedule_div")
            confidence_score += 25  # V2: Increased from 20 to 25
            
        if soup.find('table', {'class': re.compile(r'.*games.*|.*matches.*|.*fixtures.*', re.I)}):
            structural_indicators.append("games_table")
            confidence_score += 25  # V2: Increased from 20 to 25
        
        # V2: Look for streaming-specific meta tags
        streaming_meta_patterns = [
            'property="og:video"', 'property="twitter:player"',
            'name="twitter:player"', 'property="video"'
        ]
        
        for pattern in streaming_meta_patterns:
            if pattern.lower() in html_content.lower():
                structural_indicators.append(f"meta_{pattern.split('=')[0].split(':')[-1]}")
                confidence_score += 15
        
        # V2: Look for common streaming platform indicators
        platform_indicators = [
            'jwplayer', 'videojs', 'hls.js', 'dashjs', 'flowplayer',
            'plyr', 'clappr', 'video.js', 'bitmovin'
        ]
        
        for indicator in platform_indicators:
            if indicator in html_content.lower():
                structural_indicators.append(f"platform_{indicator}")
                confidence_score += 10
        
        result = {
            'success': True,
            'confidence_score': confidence_score,
            'structural_indicators': structural_indicators,
            'error': None
        }
        
        logger.debug(f"DOM fingerprinting completed: score={confidence_score}, indicators={len(structural_indicators)}")
        return result
        
    except Exception as e:
        logger.debug(f"DOM fingerprinting ERROR: {str(e)}")
        return {
            'success': False,
            'confidence_score': 0,
            'structural_indicators': [],
            'error': str(e)
        }


def verify_url(url, scout_instance=None):
    """
    V2 Complete verification pipeline that runs all verification stages with enhanced scoring.
    
    Args:
        url (str): URL to verify
        scout_instance: SignalScout instance for browser access
        
    Returns:
        dict: Complete verification result with all test outcomes
    """
    logger.info(f"Starting V2 verification pipeline for {url}")
    
    # Initialize result structure
    verification_result = {
        'url': url,
        'passed': False,
        'overall_confidence': 0,
        'probe': None,
        'content_analysis': None,
        'dom_fingerprint': None,
        'timestamp': time.time()
    }
    
    # Stage 1: Probe reachability
    probe_result = probe_reachability(url)
    verification_result['probe'] = probe_result
    
    if not probe_result['success']:
        logger.info(f"V2 Verification FAILED for {url} - not reachable")
        return verification_result
    
    # Stage 2: V2 Content analysis with dynamic content
    content_result = analyze_content(url, scout_instance=scout_instance)
    verification_result['content_analysis'] = content_result
    
    # Stage 3: V2 DOM fingerprinting with dynamic content (most critical)
    dom_result = fingerprint_dom(url, scout_instance=scout_instance)
    verification_result['dom_fingerprint'] = dom_result
    
    # V2: Enhanced confidence scoring system
    # Base Score: 10 points for reachability
    base_score = 10
    
    # Content Analysis: 0-30% contribution (reduced from 30% to allow for other factors)
    content_score = content_result.get('confidence_score', 0) if content_result['success'] else 0
    content_contribution = content_score * 0.25
    
    # DOM Fingerprinting: 0-60% contribution (weight increased as most important)
    dom_score = dom_result.get('confidence_score', 0) if dom_result['success'] else 0
    dom_contribution = dom_score * 0.65
    
    # V2: Calculate overall confidence with new weighted system
    overall_confidence = base_score + content_contribution + dom_contribution
    
    # V2: Bonus system for high-quality indicators
    bonus_points = 0
    if content_result['success'] and content_result.get('indicators', []):
        # Bonus for rich content indicators
        if len(content_result['indicators']) > 5:
            bonus_points += 10
    
    if dom_result['success'] and dom_result.get('structural_indicators', []):
        # Major bonus for strong DOM indicators
        if 'video_tags' in str(dom_result['structural_indicators']):
            bonus_points += 15
        if 'streaming_iframe' in dom_result['structural_indicators']:
            bonus_points += 10
    
    overall_confidence += bonus_points
    
    # Cap the final score
    overall_confidence = min(int(overall_confidence), 100)
    verification_result['overall_confidence'] = overall_confidence
    
    # V2: Determine pass/fail based on threshold (will be checked by scout)
    # Note: We don't set 'passed' here anymore, let the scout decide based on its threshold
    
    status = "ANALYZING" 
    logger.info(f"V2 Verification {status} for {url} - confidence: {overall_confidence}")
    logger.debug(f"  Content: {content_score} -> {content_contribution:.1f}")
    logger.debug(f"  DOM: {dom_score} -> {dom_contribution:.1f}")
    logger.debug(f"  Base + Bonus: {base_score + bonus_points}")
    
    return verification_result


if __name__ == "__main__":
    # Test the verification pipeline
    test_urls = [
        "https://www.google.com",
        "https://example.com"
    ]
    
    for url in test_urls:
        result = verify_url(url)
        print(f"\nVerification result for {url}:")
        print(f"  Passed: {result['passed']}")
        print(f"  Confidence: {result['overall_confidence']}")
        if result['content_analysis'] and result['content_analysis']['title']:
            print(f"  Title: {result['content_analysis']['title']}")