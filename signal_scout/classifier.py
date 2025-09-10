"""
AI Classifier for Signal Scout V3 - The "Judge"

This module implements machine learning-based classification of streaming sites
with comprehensive feature extraction and transparent decision logging.
"""

import re
import logging
import numpy as np
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
import pickle
import os
from urllib.parse import urlparse

# Configure logging
logger = logging.getLogger(__name__)


class StreamingSiteClassifier:
    """
    AI Classifier for identifying sports streaming websites with high accuracy.
    
    Features extracted include:
    - Technical DNA: Video/streaming elements, iframes, etc.
    - Content DNA: TF-IDF vectors of sports-related keywords
    - Structural DNA: Link density, DOM structure, etc.
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the classifier.
        
        Args:
            model_path (str): Path to saved model file
        """
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), 'scout_model.pkl')
        
        self.model_path = model_path
        self.model = None
        self.feature_names = []
        
        # Sports and streaming keywords for content analysis
        self.sports_keywords = [
            'live', 'stream', 'watch', 'nfl', 'nba', 'nhl', 'mlb', 'soccer', 
            'football', 'basketball', 'hockey', 'baseball', 'sports', 'game',
            'match', 'playoff', 'championship', 'league', 'team', 'score',
            'highlights', 'replay', 'broadcast', 'free', 'online', 'tv',
            'channel', 'video', 'player', 'espn', 'fox', 'cbs', 'nbc'
        ]
        
        # Technical streaming indicators
        self.streaming_indicators = [
            'video', 'player', 'stream', 'embed', 'iframe', 'jwplayer',
            'videojs', 'hls', 'm3u8', 'rtmp', 'dash', 'mp4'
        ]
        
        self._load_model()
    
    def _load_model(self):
        """Load the trained model if it exists."""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data['model']
                    self.feature_names = model_data.get('feature_names', [])
                logger.info(f"Loaded trained model from {self.model_path}")
            else:
                logger.warning(f"No trained model found at {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None
    
    def extract_features(self, html_content, url=""):
        """
        Extract comprehensive feature vector from HTML content and URL.
        
        Args:
            html_content (str): Full HTML content of the page
            url (str): URL of the page
            
        Returns:
            dict: Feature dictionary with named features and values
        """
        features = {}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text().lower()
            url_lower = url.lower()
            
            # Technical DNA Features
            features['has_video_tag'] = len(soup.find_all('video')) > 0
            features['has_iframe'] = len(soup.find_all('iframe')) > 0
            features['iframe_count'] = len(soup.find_all('iframe'))
            features['has_embed'] = len(soup.find_all('embed')) > 0
            features['has_object'] = len(soup.find_all('object')) > 0
            
            # Look for streaming-specific elements
            features['has_jwplayer'] = 'jwplayer' in text_content
            features['has_videojs'] = 'video.js' in text_content or 'videojs' in text_content
            features['has_hls_reference'] = 'm3u8' in text_content or 'hls' in text_content
            features['has_streaming_js'] = any(indicator in text_content for indicator in self.streaming_indicators)
            
            # Content DNA Features - Sports keyword density
            total_words = len(text_content.split())
            if total_words > 0:
                for keyword in self.sports_keywords:
                    count = text_content.count(keyword)
                    features[f'keyword_density_{keyword}'] = count / total_words
            else:
                for keyword in self.sports_keywords:
                    features[f'keyword_density_{keyword}'] = 0
            
            # Overall sports keyword density
            total_sports_keywords = sum(text_content.count(kw) for kw in self.sports_keywords)
            features['total_sports_keyword_density'] = total_sports_keywords / max(total_words, 1)
            
            # Structural DNA Features
            features['link_count'] = len(soup.find_all('a'))
            features['external_link_count'] = self._count_external_links(soup, url)
            features['dom_depth'] = self._calculate_dom_depth(soup)
            features['title_length'] = len(soup.title.get_text() if soup.title else "")
            
            # URL-based features
            parsed_url = urlparse(url)
            features['url_has_sports_keyword'] = any(kw in url_lower for kw in self.sports_keywords)
            features['url_has_stream_keyword'] = any(kw in url_lower for kw in ['stream', 'live', 'watch', 'tv'])
            features['domain_length'] = len(parsed_url.netloc)
            features['path_depth'] = len([p for p in parsed_url.path.split('/') if p])
            
            # Content length and structure indicators
            features['html_size'] = len(html_content)
            features['text_to_html_ratio'] = len(text_content) / max(len(html_content), 1)
            features['script_count'] = len(soup.find_all('script'))
            features['css_count'] = len(soup.find_all('style')) + len(soup.find_all('link', rel='stylesheet'))
            
            # Meta tag analysis
            meta_description = soup.find('meta', attrs={'name': 'description'})
            if meta_description:
                desc_content = (meta_description.get('content') or '').lower()
                features['meta_has_sports'] = any(kw in desc_content for kw in self.sports_keywords)
            else:
                features['meta_has_sports'] = False
            
            # Title analysis
            title_text = (soup.title.get_text() if soup.title else '').lower()
            features['title_has_sports'] = any(kw in title_text for kw in self.sports_keywords)
            features['title_has_stream'] = any(kw in title_text for kw in ['stream', 'live', 'watch'])
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            # Return default features on error
            features = {name: 0 for name in self._get_default_feature_names()}
        
        return features
    
    def _count_external_links(self, soup, current_url):
        """Count external links on the page."""
        try:
            current_domain = urlparse(current_url).netloc
            external_count = 0
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http'):
                    link_domain = urlparse(href).netloc
                    if link_domain != current_domain:
                        external_count += 1
            
            return external_count
        except:
            return 0
    
    def _calculate_dom_depth(self, soup):
        """Calculate the maximum depth of the DOM tree."""
        try:
            def get_depth(element, current_depth=0):
                if element.children:
                    return max(get_depth(child, current_depth + 1) 
                             for child in element.children 
                             if hasattr(child, 'children'))
                return current_depth
            
            return get_depth(soup)
        except:
            return 0
    
    def _get_default_feature_names(self):
        """Get list of default feature names for error handling."""
        features = ['has_video_tag', 'has_iframe', 'iframe_count', 'has_embed', 'has_object',
                   'has_jwplayer', 'has_videojs', 'has_hls_reference', 'has_streaming_js',
                   'total_sports_keyword_density', 'link_count', 'external_link_count',
                   'dom_depth', 'title_length', 'url_has_sports_keyword', 'url_has_stream_keyword',
                   'domain_length', 'path_depth', 'html_size', 'text_to_html_ratio',
                   'script_count', 'css_count', 'meta_has_sports', 'title_has_sports', 'title_has_stream']
        
        # Add keyword density features
        for keyword in self.sports_keywords:
            features.append(f'keyword_density_{keyword}')
        
        return features
    
    def classify_page(self, html_content, url=""):
        """
        Classify a page as streaming site or not with probability score.
        
        Args:
            html_content (str): HTML content of the page
            url (str): URL of the page
            
        Returns:
            dict: Classification result with probability and feature analysis
        """
        if not self.model:
            logger.warning("No trained model available for classification")
            return {
                'is_streaming_site': False,
                'probability': 0.0,
                'confidence': 'low',
                'error': 'No trained model available'
            }
        
        try:
            # Extract features
            features = self.extract_features(html_content, url)
            
            # Convert to feature vector
            feature_vector = self._features_to_vector(features)
            
            # Make prediction
            prediction = self.model.predict([feature_vector])[0]
            probability = self.model.predict_proba([feature_vector])[0]
            
            # Get probability for positive class (streaming site)
            positive_class_prob = probability[1] if len(probability) > 1 else probability[0]
            
            # Determine confidence level
            confidence = self._get_confidence_level(positive_class_prob)
            
            # Log decision reasoning
            self._log_classification_reasoning(features, positive_class_prob, url)
            
            result = {
                'is_streaming_site': bool(prediction),
                'probability': float(positive_class_prob),
                'confidence': confidence,
                'features_analyzed': len(features),
                'key_features': self._get_key_features(features),
                'error': None
            }
            
            logger.info(f"Classification result for {url}: {positive_class_prob:.3f} probability "
                       f"({'streaming' if prediction else 'not streaming'})")
            
            return result
            
        except Exception as e:
            logger.error(f"Classification error for {url}: {e}")
            return {
                'is_streaming_site': False,
                'probability': 0.0,
                'confidence': 'error',
                'error': str(e)
            }
    
    def _features_to_vector(self, features):
        """Convert feature dictionary to vector array."""
        # Ensure consistent feature ordering
        if self.feature_names:
            vector = [features.get(name, 0) for name in self.feature_names]
        else:
            # Use sorted keys for consistent ordering
            sorted_keys = sorted(features.keys())
            vector = [features[key] for key in sorted_keys]
        
        return np.array(vector, dtype=float)
    
    def _get_confidence_level(self, probability):
        """Map probability to confidence level."""
        if probability >= 0.9:
            return 'very_high'
        elif probability >= 0.7:
            return 'high'
        elif probability >= 0.5:
            return 'medium'
        elif probability >= 0.3:
            return 'low'
        else:
            return 'very_low'
    
    def _get_key_features(self, features):
        """Identify the most important features that influenced the decision."""
        key_features = {}
        
        # Technical features
        if features.get('has_video_tag', False):
            key_features['video_elements'] = True
        if features.get('iframe_count', 0) > 0:
            key_features['iframe_count'] = features['iframe_count']
        if features.get('has_streaming_js', False):
            key_features['streaming_technology'] = True
        
        # Content features
        sports_density = features.get('total_sports_keyword_density', 0)
        if sports_density > 0.01:  # More than 1% sports keywords
            key_features['sports_content_density'] = sports_density
        
        # URL features
        if features.get('url_has_sports_keyword', False):
            key_features['sports_in_url'] = True
        if features.get('url_has_stream_keyword', False):
            key_features['streaming_in_url'] = True
        
        return key_features
    
    def _log_classification_reasoning(self, features, probability, url):
        """Log detailed reasoning for the classification decision."""
        reasoning_parts = []
        
        # Technical indicators
        if features.get('has_video_tag', False):
            reasoning_parts.append("has video tags")
        if features.get('iframe_count', 0) > 0:
            reasoning_parts.append(f"{features['iframe_count']} iframes")
        if features.get('has_streaming_js', False):
            reasoning_parts.append("streaming JavaScript detected")
        
        # Content indicators
        sports_density = features.get('total_sports_keyword_density', 0)
        if sports_density > 0.01:
            reasoning_parts.append(f"sports keyword density: {sports_density:.3f}")
        
        # URL indicators
        if features.get('url_has_sports_keyword', False):
            reasoning_parts.append("sports keywords in URL")
        if features.get('url_has_stream_keyword', False):
            reasoning_parts.append("streaming keywords in URL")
        
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "low confidence indicators"
        
        logger.info(f"V3 AI Classification - {url} -> {probability:.3f} confidence "
                   f"({reasoning})")


def create_default_classifier():
    """Create a classifier instance with default settings."""
    return StreamingSiteClassifier()