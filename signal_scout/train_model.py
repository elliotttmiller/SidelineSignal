#!/usr/bin/env python3
"""
Signal Scout V3 - Model Training Script

This script trains the AI classifier model using the curated training dataset
and saves the trained model for use by the live Scout system.
"""

import os
import logging
import pickle
import requests
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
from playwright.sync_api import sync_playwright

from classifier import StreamingSiteClassifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Trainer class for the Signal Scout V3 AI classification model.
    """
    
    def __init__(self, positive_samples_file='positive_samples.txt', 
                 negative_samples_file='negative_samples.txt',
                 model_output_path='scout_model.pkl'):
        """
        Initialize the model trainer.
        
        Args:
            positive_samples_file (str): Path to positive sample URLs file
            negative_samples_file (str): Path to negative sample URLs file
            model_output_path (str): Path where to save the trained model
        """
        self.positive_samples_file = positive_samples_file
        self.negative_samples_file = negative_samples_file
        self.model_output_path = model_output_path
        self.classifier = StreamingSiteClassifier()
        
        # Initialize browser for dynamic content fetching
        self.playwright = None
        self.browser = None
        self.context = None
        self._initialize_browser()
    
    def _initialize_browser(self):
        """Initialize Playwright browser for content fetching."""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=True)
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            logger.info("Browser initialized for training data collection")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            self.playwright = None
            self.browser = None
            self.context = None
    
    def _cleanup_browser(self):
        """Clean up browser resources."""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.error(f"Error cleaning up browser: {e}")
    
    def _fetch_page_content(self, url, timeout=10):
        """
        Fetch dynamic page content using Playwright with fallback to requests.
        
        Args:
            url (str): URL to fetch
            timeout (int): Timeout in seconds
            
        Returns:
            str: HTML content or None if failed
        """
        # Try Playwright first for dynamic content
        if self.context:
            try:
                page = self.context.new_page()
                page.goto(url, timeout=timeout * 1000, wait_until='domcontentloaded')
                page.wait_for_timeout(2000)  # Wait for dynamic content
                content = page.content()
                page.close()
                logger.debug(f"Fetched content via Playwright: {url}")
                return content
            except Exception as e:
                logger.debug(f"Playwright failed for {url}: {e}")
                try:
                    page.close()
                except:
                    pass
        
        # Fallback to requests
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            logger.debug(f"Fetched content via requests: {url}")
            return response.text
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None
    
    def _load_sample_urls(self, filename):
        """Load URLs from a sample file."""
        urls = []
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        urls.append(line)
            logger.info(f"Loaded {len(urls)} URLs from {filename}")
        except FileNotFoundError:
            logger.error(f"Sample file not found: {filename}")
        except Exception as e:
            logger.error(f"Error loading sample file {filename}: {e}")
        
        return urls
    
    def collect_training_data(self):
        """
        Collect training data by fetching content from sample URLs.
        
        Returns:
            tuple: (features_list, labels_list)
        """
        logger.info("Starting training data collection...")
        
        # Load sample URLs
        positive_urls = self._load_sample_urls(self.positive_samples_file)
        negative_urls = self._load_sample_urls(self.negative_samples_file)
        
        if not positive_urls or not negative_urls:
            raise ValueError("Could not load sample URLs. Check sample files exist.")
        
        features_list = []
        labels_list = []
        
        # Process positive samples
        logger.info(f"Processing {len(positive_urls)} positive samples...")
        for i, url in enumerate(positive_urls, 1):
            logger.info(f"Fetching positive sample {i}/{len(positive_urls)}: {url}")
            content = self._fetch_page_content(url)
            
            if content:
                try:
                    features = self.classifier.extract_features(content, url)
                    features_list.append(features)
                    labels_list.append(1)  # Positive label
                    logger.debug(f"Extracted features for positive sample: {url}")
                except Exception as e:
                    logger.error(f"Feature extraction failed for {url}: {e}")
            
            # Rate limiting
            time.sleep(1)
        
        # Process negative samples
        logger.info(f"Processing {len(negative_urls)} negative samples...")
        for i, url in enumerate(negative_urls, 1):
            logger.info(f"Fetching negative sample {i}/{len(negative_urls)}: {url}")
            content = self._fetch_page_content(url)
            
            if content:
                try:
                    features = self.classifier.extract_features(content, url)
                    features_list.append(features)
                    labels_list.append(0)  # Negative label
                    logger.debug(f"Extracted features for negative sample: {url}")
                except Exception as e:
                    logger.error(f"Feature extraction failed for {url}: {e}")
            
            # Rate limiting
            time.sleep(1)
        
        logger.info(f"Training data collection complete: {len(features_list)} samples")
        return features_list, labels_list
    
    def _features_to_matrix(self, features_list):
        """Convert list of feature dictionaries to numpy matrix."""
        if not features_list:
            return np.array([]), []
        
        # Get all unique feature names
        all_feature_names = set()
        for features in features_list:
            all_feature_names.update(features.keys())
        
        feature_names = sorted(list(all_feature_names))
        
        # Convert to matrix
        matrix = []
        for features in features_list:
            row = [features.get(name, 0) for name in feature_names]
            matrix.append(row)
        
        return np.array(matrix, dtype=float), feature_names
    
    def train_model(self, features_list, labels_list):
        """
        Train the classification model.
        
        Args:
            features_list (list): List of feature dictionaries
            labels_list (list): List of labels (0 or 1)
            
        Returns:
            tuple: (trained_model, feature_names, performance_metrics)
        """
        logger.info("Starting model training...")
        
        # Convert to matrix format
        X, feature_names = self._features_to_matrix(features_list)
        y = np.array(labels_list)
        
        if len(X) == 0:
            raise ValueError("No training data available")
        
        logger.info(f"Training matrix shape: {X.shape}")
        logger.info(f"Feature names: {len(feature_names)}")
        logger.info(f"Positive samples: {sum(y)}, Negative samples: {len(y) - sum(y)}")
        
        # Split data for validation
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Try multiple models and select the best
        models = {
            'RandomForest': RandomForestClassifier(
                n_estimators=100, 
                random_state=42,
                class_weight='balanced'
            ),
            'LogisticRegression': LogisticRegression(
                random_state=42,
                class_weight='balanced',
                max_iter=1000
            )
        }
        
        best_model = None
        best_score = 0
        best_model_name = ""
        
        for model_name, model in models.items():
            logger.info(f"Training {model_name}...")
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1')
            avg_score = np.mean(cv_scores)
            
            logger.info(f"{model_name} CV F1 Score: {avg_score:.3f} (+/- {np.std(cv_scores) * 2:.3f})")
            
            if avg_score > best_score:
                best_score = avg_score
                best_model = model
                best_model_name = model_name
        
        # Train the best model on full training set
        logger.info(f"Best model: {best_model_name} with F1 score: {best_score:.3f}")
        best_model.fit(X_train, y_train)
        
        # Evaluate on test set
        y_pred = best_model.predict(X_test)
        
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, y_pred))
        
        logger.info("\nConfusion Matrix:")
        logger.info(confusion_matrix(y_test, y_pred))
        
        # Performance metrics
        performance_metrics = {
            'model_type': best_model_name,
            'cv_f1_score': best_score,
            'test_accuracy': best_model.score(X_test, y_test),
            'feature_count': len(feature_names),
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        return best_model, feature_names, performance_metrics
    
    def save_model(self, model, feature_names, performance_metrics):
        """Save the trained model and metadata."""
        model_data = {
            'model': model,
            'feature_names': feature_names,
            'performance_metrics': performance_metrics,
            'version': '3.0'
        }
        
        try:
            with open(self.model_output_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved successfully to {self.model_output_path}")
            logger.info(f"Model performance: {performance_metrics}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise
    
    def train_and_save(self):
        """Complete training pipeline: collect data, train, and save model."""
        try:
            # Collect training data
            features_list, labels_list = self.collect_training_data()
            
            if len(features_list) < 10:
                logger.warning(f"Very small training set: {len(features_list)} samples")
            
            # Train model
            model, feature_names, performance_metrics = self.train_model(features_list, labels_list)
            
            # Save model
            self.save_model(model, feature_names, performance_metrics)
            
            logger.info("Training pipeline completed successfully!")
            
        except Exception as e:
            logger.error(f"Training pipeline failed: {e}")
            raise
        finally:
            # Clean up resources
            self._cleanup_browser()


def main():
    """Main training function."""
    try:
        trainer = ModelTrainer()
        trainer.train_and_save()
    except KeyboardInterrupt:
        logger.info("Training interrupted by user")
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise


if __name__ == "__main__":
    main()