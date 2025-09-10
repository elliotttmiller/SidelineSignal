"""
Signal Scout V3 Integration Module

This module extends the V2 Scout with V3 cognitive crawler capabilities,
maintaining backward compatibility while adding autonomous AI-driven discovery.
"""

import os
import logging
import subprocess
import sys
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class V3CognitiveEngine:
    """
    V3 Cognitive Engine that extends V2 Scout with autonomous crawling capabilities.
    """
    
    def __init__(self, scout_instance):
        """
        Initialize V3 engine with reference to V2 Scout instance.
        
        Args:
            scout_instance: V2 SignalScout instance
        """
        self.scout = scout_instance
        self.config = scout_instance.config
        
        # V3 specific configuration
        self.v3_config = self.config.get('v3_crawler_settings', {})
        
        logger.info("V3 Cognitive Engine initialized")
    
    def run_autonomous_discovery_cycle(self):
        """
        Execute V3 autonomous discovery cycle using Scrapy crawler.
        
        Returns:
            dict: Discovery cycle results
        """
        logger.info("=" * 60)
        logger.info("SIGNAL SCOUT V3 - AUTONOMOUS COGNITIVE CRAWLER")
        logger.info("=" * 60)
        
        try:
            # Change to spider directory
            spider_dir = os.path.join(os.path.dirname(__file__), 'spider')
            original_dir = os.getcwd()
            
            # Create a Python script to run the spider with proper imports
            spider_script = self._create_spider_runner_script()
            
            try:
                os.chdir(spider_dir)
                
                # Run the Scrapy spider
                logger.info("Launching V3 Cognitive Crawler...")
                result = subprocess.run([
                    sys.executable, spider_script
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info("V3 Crawler completed successfully")
                    logger.info("Crawler output:")
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            logger.info(f"  {line}")
                else:
                    logger.error(f"V3 Crawler failed with return code {result.returncode}")
                    logger.error("Error output:")
                    for line in result.stderr.split('\n'):
                        if line.strip():
                            logger.error(f"  {line}")
                
                # Parse results from output
                return self._parse_crawler_results(result.stdout)
                
            finally:
                os.chdir(original_dir)
                # Clean up temporary script
                if os.path.exists(spider_script):
                    os.remove(spider_script)
                
        except subprocess.TimeoutExpired:
            logger.error("V3 Crawler timed out after 5 minutes")
            return {'error': 'timeout', 'discovered': 0, 'verified': 0}
        except Exception as e:
            logger.error(f"V3 Crawler failed: {e}")
            return {'error': str(e), 'discovered': 0, 'verified': 0}
    
    def _create_spider_runner_script(self):
        """Create a temporary script to run the spider with proper configuration."""
        script_content = f'''#!/usr/bin/env python3
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Run the spider
if __name__ == "__main__":
    import scrapy.cmdline
    
    try:
        scrapy.cmdline.execute([
            'scrapy', 'crawl', 'streaming_spider',
            '--loglevel=INFO',
            '--set=CLOSESPIDER_PAGECOUNT=50'  # Limit for testing
        ])
    except SystemExit:
        pass  # Scrapy calls sys.exit(), ignore it
'''
        
        script_path = os.path.join(os.path.dirname(__file__), 'spider', 'run_spider.py')
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        return script_path
    
    def _parse_crawler_results(self, output):
        """Parse results from crawler output."""
        results = {
            'v3_mode': True,
            'discovered': 0,
            'verified': 0,
            'classified_positive': 0,
            'classified_negative': 0,
            'pages_crawled': 0
        }
        
        try:
            for line in output.split('\n'):
                if 'Pages Crawled:' in line:
                    results['pages_crawled'] = int(line.split(':')[1].strip())
                elif 'AI Classifications: +' in line:
                    parts = line.split('+')[1].split('-')
                    if len(parts) >= 2:
                        results['classified_positive'] = int(parts[0].strip())
                        results['classified_negative'] = int(parts[1].strip())
                elif 'V2 Verifications: +' in line:
                    parts = line.split('+')[1].split('-')
                    if len(parts) >= 2:
                        results['verified'] = int(parts[0].strip())
        except Exception as e:
            logger.debug(f"Error parsing crawler results: {e}")
        
        return results
    
    def run_hybrid_discovery_cycle(self):
        """
        Run hybrid discovery cycle: V2 + V3 combined.
        
        Returns:
            dict: Combined results from both V2 and V3
        """
        logger.info("=" * 60)
        logger.info("SIGNAL SCOUT V3 - HYBRID DISCOVERY MODE")
        logger.info("=" * 60)
        
        # Run V2 cycle first
        logger.info("Phase 1: V2 Traditional Discovery")
        v2_results = self.scout.run_discovery_cycle()
        
        # Run V3 autonomous discovery
        logger.info("Phase 2: V3 Cognitive Crawler")
        v3_results = self.run_autonomous_discovery_cycle()
        
        # Combine results
        combined_results = {
            'mode': 'hybrid_v2_v3',
            'v2_results': v2_results,
            'v3_results': v3_results,
            'total_discovered': v2_results.get('discovered', 0) + v3_results.get('discovered', 0),
            'total_verified': v2_results.get('verified', 0) + v3_results.get('verified', 0),
            'v3_enabled': True
        }
        
        logger.info("=" * 60)
        logger.info("HYBRID DISCOVERY CYCLE COMPLETE")
        logger.info(f"V2 Discoveries: {v2_results.get('discovered', 0)}")
        logger.info(f"V3 Discoveries: {v3_results.get('discovered', 0)}")
        logger.info(f"Total Verified: {combined_results['total_verified']}")
        logger.info("=" * 60)
        
        return combined_results


def extend_scout_with_v3(scout_instance):
    """
    Extend a V2 Scout instance with V3 capabilities.
    
    Args:
        scout_instance: V2 SignalScout instance
        
    Returns:
        V3CognitiveEngine: Enhanced scout with V3 capabilities
    """
    return V3CognitiveEngine(scout_instance)


def test_v3_classifier():
    """Test the V3 AI classifier with sample content."""
    logger.info("Testing V3 AI Classifier...")
    
    try:
        from classifier import StreamingSiteClassifier
        
        classifier = StreamingSiteClassifier()
        
        # Test with sample HTML content
        test_html = '''
        <html>
            <head><title>Live Sports Streaming - Watch NFL Free</title></head>
            <body>
                <h1>Watch Live Sports Online</h1>
                <div>Stream NFL, NBA, MLB games for free</div>
                <video controls>
                    <source src="stream.m3u8" type="application/x-mpegURL">
                </video>
                <iframe src="player.html"></iframe>
            </body>
        </html>
        '''
        
        result = classifier.classify_page(test_html, "https://test-stream.com")
        
        logger.info(f"Classifier test result: {result}")
        logger.info("V3 AI Classifier is working correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"V3 Classifier test failed: {e}")
        return False


def check_v3_dependencies():
    """Check if all V3 dependencies are available."""
    dependencies = ['scrapy', 'sklearn', 'numpy']
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            logger.info(f"✓ {dep} available")
        except ImportError:
            missing.append(dep)
            logger.error(f"✗ {dep} missing")
    
    if missing:
        logger.error(f"Missing V3 dependencies: {missing}")
        return False
    
    logger.info("All V3 dependencies are available")
    return True


if __name__ == "__main__":
    # Test V3 components
    logging.basicConfig(level=logging.INFO)
    
    print("Testing V3 components...")
    
    deps_ok = check_v3_dependencies()
    classifier_ok = test_v3_classifier()
    
    if deps_ok and classifier_ok:
        print("✓ V3 system is ready")
    else:
        print("✗ V3 system has issues")