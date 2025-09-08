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


def analyze_content(url, timeout=10):
    """
    Content Analysis: Examines page title and meta content for streaming indicators.
    
    Args:
        url (str): URL to analyze
        timeout (int): Request timeout in seconds
        
    Returns:
        dict: Analysis result with confidence score and indicators
    """
    logger.debug(f"Analyzing content for {url}")
    
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
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ''
        
        # Combine text for analysis
        content_text = f"{title} {description}".lower()
        
        # Define streaming indicators with weights
        indicators = []
        confidence_score = 0
        
        streaming_keywords = {
            'stream': 20,
            'watch': 20,
            'live': 15,
            'movie': 15,
            'tv': 15,
            'sport': 15,
            'free': 10,
            'online': 10,
            'hd': 5,
            'video': 10,
            'player': 10,
            'schedule': 15,
            'games': 10,
            'nfl': 10,
            'nba': 10,
            'soccer': 10,
            'football': 10
        }
        
        for keyword, weight in streaming_keywords.items():
            if keyword in content_text:
                indicators.append(f"keyword_{keyword}")
                confidence_score += weight
        
        # Bonus for multiple indicators
        if len(indicators) > 3:
            confidence_score += 10
            
        # Cap the score at 100
        confidence_score = min(confidence_score, 100)
        
        result = {
            'success': True,
            'confidence_score': confidence_score,
            'indicators': indicators,
            'title': title,
            'error': None
        }
        
        logger.debug(f"Content analysis for {url}: score={confidence_score}, indicators={len(indicators)}")
        return result
        
    except Exception as e:
        logger.debug(f"Content analysis ERROR: {url} -> {str(e)}")
        return {
            'success': False,
            'confidence_score': 0,
            'indicators': [],
            'title': None,
            'error': str(e)
        }


def fingerprint_dom(url, timeout=10):
    """
    DOM Fingerprinting: The most critical test that examines HTML structure for streaming indicators.
    
    Args:
        url (str): URL to fingerprint
        timeout (int): Request timeout in seconds
        
    Returns:
        dict: Fingerprinting result with structural indicators
    """
    logger.debug(f"DOM fingerprinting for {url}")
    
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
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        structural_indicators = []
        confidence_score = 0
        
        # Look for video-related elements
        video_tags = soup.find_all('video')
        if video_tags:
            structural_indicators.append(f"video_tags_{len(video_tags)}")
            confidence_score += 30
        
        # Look for iframe elements (common in streaming sites)
        iframes = soup.find_all('iframe')
        if iframes:
            structural_indicators.append(f"iframes_{len(iframes)}")
            confidence_score += 25
            
            # Check iframe sources for streaming indicators
            for iframe in iframes:
                src = iframe.get('src', '').lower()
                if any(keyword in src for keyword in ['player', 'stream', 'video', 'embed']):
                    structural_indicators.append("streaming_iframe")
                    confidence_score += 15
                    break
        
        # Look for divs with streaming-related IDs or classes
        streaming_selectors = [
            {'id': 'player'}, {'id': 'video-player'}, {'id': 'stream'},
            {'id': 'schedule'}, {'id': 'games'}, {'id': 'matches'},
            {'class': 'player'}, {'class': 'video-player'}, {'class': 'stream'},
            {'class': 'schedule'}, {'class': 'games'}, {'class': 'matches'}
        ]
        
        for selector in streaming_selectors:
            elements = soup.find_all('div', selector)
            if elements:
                key = list(selector.keys())[0]
                value = list(selector.values())[0]
                structural_indicators.append(f"{key}_{value}")
                confidence_score += 10
        
        # Look for script tags that might contain player initialization
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                script_content = script.string.lower()
                if any(keyword in script_content for keyword in ['player', 'video', 'stream', 'jwplayer']):
                    structural_indicators.append("streaming_script")
                    confidence_score += 15
                    break
        
        # Look for common streaming site patterns
        if soup.find('div', {'class': re.compile(r'.*schedule.*', re.I)}):
            structural_indicators.append("schedule_div")
            confidence_score += 20
            
        if soup.find('table', {'class': re.compile(r'.*games.*|.*matches.*', re.I)}):
            structural_indicators.append("games_table")
            confidence_score += 20
        
        # Cap the score at 100
        confidence_score = min(confidence_score, 100)
        
        result = {
            'success': True,
            'confidence_score': confidence_score,
            'structural_indicators': structural_indicators,
            'error': None
        }
        
        logger.debug(f"DOM fingerprinting for {url}: score={confidence_score}, indicators={len(structural_indicators)}")
        return result
        
    except Exception as e:
        logger.debug(f"DOM fingerprinting ERROR: {url} -> {str(e)}")
        return {
            'success': False,
            'confidence_score': 0,
            'structural_indicators': [],
            'error': str(e)
        }


def verify_url(url):
    """
    Complete verification pipeline that runs all verification stages.
    
    Args:
        url (str): URL to verify
        
    Returns:
        dict: Complete verification result with all test outcomes
    """
    logger.info(f"Starting verification pipeline for {url}")
    
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
        logger.info(f"Verification FAILED for {url} - not reachable")
        return verification_result
    
    # Stage 2: Content analysis
    content_result = analyze_content(url)
    verification_result['content_analysis'] = content_result
    
    # Stage 3: DOM fingerprinting (most critical)
    dom_result = fingerprint_dom(url)
    verification_result['dom_fingerprint'] = dom_result
    
    # Calculate overall confidence score
    # DOM fingerprinting is weighted most heavily (60%)
    # Content analysis is secondary (30%)
    # Reachability is baseline (10%)
    
    dom_score = dom_result.get('confidence_score', 0) if dom_result['success'] else 0
    content_score = content_result.get('confidence_score', 0) if content_result['success'] else 0
    
    overall_confidence = (
        (dom_score * 0.6) +
        (content_score * 0.3) +
        (10 * 0.1)  # Base points for reachability
    )
    
    verification_result['overall_confidence'] = int(overall_confidence)
    
    # Consider verification passed if confidence >= 40
    verification_result['passed'] = overall_confidence >= 40
    
    status = "PASSED" if verification_result['passed'] else "FAILED"
    logger.info(f"Verification {status} for {url} - confidence: {int(overall_confidence)}")
    
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