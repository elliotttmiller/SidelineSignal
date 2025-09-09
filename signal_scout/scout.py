"""
Signal Scout - Autonomous Discovery and Verification Engine

This is the main orchestration script that coordinates URL discovery,
verification, and database storage for the SidelineSignal monitoring system.
"""

import sqlite3
import os
import logging
import json
from datetime import datetime, timedelta
import time
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
import atexit

from hunters import discover_urls
from verification import verify_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scout.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SignalScout:
    """
    Main Scout engine that orchestrates the discovery and verification process.
    """
    
    def __init__(self, db_path=None, config_path=None):
        """
        Initialize the Signal Scout.
        
        Args:
            db_path (str): Path to the SQLite database (default: ../shared_data/sites.db)
            config_path (str): Path to the configuration file (default: ./scout_config.json)
        """
        if db_path is None:
            # Default path relative to scout directory
            self.db_path = os.path.join(os.path.dirname(__file__), '..', 'shared_data', 'sites.db')
        else:
            self.db_path = db_path
            
        self.db_path = os.path.abspath(self.db_path)
        
        if config_path is None:
            self.config_path = os.path.join(os.path.dirname(__file__), 'scout_config.json')
        else:
            self.config_path = config_path
        
        # Load configuration
        self.config = self._load_configuration()
        
        # Initialize V2 Headless Browser System
        self.playwright = None
        self.browser = None
        self.context = None
        self._initialize_browser()
        
        logger.info(f"Signal Scout V2 initialized with database: {self.db_path}")
        logger.info(f"Configuration loaded from: {self.config_path}")
        logger.info("Headless browser system active")
        
        # Ensure database exists and has correct schema
        self._ensure_database()
        
        # Register cleanup function
        atexit.register(self._cleanup_browser)
    
    def _initialize_browser(self):
        """
        Initialize the Playwright browser for dynamic content analysis.
        """
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            logger.info("Headless browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            # Fallback to requests-only mode if browser fails
            self.playwright = None
            self.browser = None
            self.context = None
    
    def _cleanup_browser(self):
        """
        Clean up browser resources on exit.
        """
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.debug("Browser resources cleaned up")
        except Exception as e:
            logger.debug(f"Error during browser cleanup: {e}")
    
    def get_dynamic_page_content(self, url, timeout=10):
        """
        V2 Feature: Get fully rendered page content using headless browser.
        
        Args:
            url (str): URL to fetch
            timeout (int): Timeout in seconds
            
        Returns:
            dict: Result containing HTML content and metadata
        """
        if not self.context:
            logger.warning("Browser not available, falling back to requests")
            return None
            
        try:
            page = self.context.new_page()
            
            # Navigate with timeout
            page.goto(url, timeout=timeout * 1000, wait_until='domcontentloaded')
            
            # Wait for additional dynamic content
            page.wait_for_timeout(2000)
            
            # Get fully rendered content
            content = page.content()
            title = page.title()
            
            # Get page metadata
            result = {
                'success': True,
                'content': content,
                'title': title,
                'url': page.url,  # Final URL after redirects
                'error': None
            }
            
            page.close()
            logger.debug(f"Successfully fetched dynamic content for {url}")
            return result
            
        except Exception as e:
            logger.debug(f"Failed to fetch dynamic content for {url}: {e}")
            if 'page' in locals():
                try:
                    page.close()
                except:
                    pass
            return {
                'success': False,
                'content': None,
                'title': None,
                'url': url,
                'error': str(e)
            }
    
    def _load_configuration(self):
        """
        Load configuration from JSON file.
        
        Returns:
            dict: Configuration dictionary
        """
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info("Configuration loaded successfully")
            return config
        except FileNotFoundError:
            logger.warning(f"Configuration file not found at {self.config_path}, using default values")
            return {
                "operational_parameters": {
                    "aggregator_urls": ["https://github.com/fmhy/FMHYedit/wiki/📺-Movies---TV"],
                    "permutation_bases": ["streameast", "sportssurge", "freestreams", "watchseries", "moviehd"],
                    "permutation_tlds": [".app", ".io", ".live", ".gg", ".net", ".org", ".tv", ".me", ".co", ".cc"]
                },
                "discovery_settings": {
                    "max_concurrent_verifications": 10,
                    "request_timeout": 5,
                    "verification_confidence_threshold": 50
                },
                "maintenance_settings": {
                    "deactivation_hours": 24,
                    "max_failed_attempts": 3,
                    "cleanup_stale_sites": True
                }
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
    
    def _ensure_database(self):
        """
        Ensure the database exists with the correct schema.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if sites table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='sites'
            """)
            
            if not cursor.fetchone():
                logger.info("Creating sites table...")
                cursor.execute('''
                    CREATE TABLE sites (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        url TEXT UNIQUE,
                        source TEXT,
                        last_verified DATETIME,
                        confidence_score INTEGER,
                        is_active BOOLEAN,
                        status TEXT DEFAULT 'active'
                    )
                ''')
                conn.commit()
            else:
                # Check if status column exists, add it if not (V2 upgrade)
                cursor.execute("PRAGMA table_info(sites)")
                columns = [col[1] for col in cursor.fetchall()]
                if 'status' not in columns:
                    logger.info("Adding status column for V2 upgrade...")
                    cursor.execute('ALTER TABLE sites ADD COLUMN status TEXT DEFAULT "active"')
                    # Update existing active sites to have 'active' status
                    cursor.execute('UPDATE sites SET status = "active" WHERE is_active = 1')
                    cursor.execute('UPDATE sites SET status = "inactive" WHERE is_active = 0')
                    conn.commit()
                
            conn.close()
            logger.info("Database schema verified")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _extract_site_name(self, url):
        """
        Extract a site name from URL.
        
        Args:
            url (str): URL to extract name from
            
        Returns:
            str: Extracted site name
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove common prefixes
            for prefix in ['www.', 'm.', 'mobile.']:
                if domain.startswith(prefix):
                    domain = domain[len(prefix):]
                    break
            
            # Take the main domain name (before the TLD)
            parts = domain.split('.')
            if len(parts) >= 2:
                return parts[0].title()
            else:
                return domain.title()
                
        except Exception:
            return url
    
    def _get_existing_urls(self):
        """
        Get set of URLs that already exist in the database.
        
        Returns:
            set: Set of existing URLs
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT url FROM sites")
            existing_urls = {row[0] for row in cursor.fetchall()}
            
            conn.close()
            return existing_urls
            
        except Exception as e:
            logger.error(f"Failed to get existing URLs: {e}")
            return set()
    
    def _store_verified_site(self, url, verification_result):
        """
        Store or update a verified site in the database.
        
        Args:
            url (str): The URL that was verified
            verification_result (dict): Result from verification pipeline
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            site_name = self._extract_site_name(url)
            confidence_score = verification_result.get('overall_confidence', 0)
            timestamp = datetime.now()
            
            # V2: Use threshold from config
            threshold = self.config.get('discovery_settings', {}).get('verification_confidence_threshold', 50)
            is_active = confidence_score >= threshold
            status = 'active' if is_active else 'inactive'
            
            # Try to update existing entry first
            cursor.execute("""
                UPDATE sites 
                SET last_verified = ?, confidence_score = ?, is_active = ?, status = ?
                WHERE url = ?
            """, (timestamp, confidence_score, is_active, status, url))
            
            if cursor.rowcount == 0:
                # Insert new entry
                cursor.execute("""
                    INSERT INTO sites (name, url, source, last_verified, confidence_score, is_active, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (site_name, url, 'scout_discovery', timestamp, confidence_score, is_active, status))
                logger.info(f"Added new site: {site_name} ({url}) - confidence: {confidence_score}, status: {status}")
            else:
                logger.info(f"Updated existing site: {site_name} ({url}) - confidence: {confidence_score}, status: {status}")
                
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store site {url}: {e}")
    
    def _quarantine_failed_sites(self, failed_urls):
        """
        V2 Feature: Mark sites for quarantine if they fail verification.
        
        Args:
            failed_urls (list): List of URLs that failed verification
            
        Returns:
            dict: Statistics about quarantine actions
        """
        if not failed_urls:
            return {'quarantined': 0, 'reactivated': 0}
            
        quarantined_count = 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            max_failed_attempts = self.config.get('maintenance_settings', {}).get('max_failed_attempts', 3)
            
            for url in failed_urls:
                # Check if site exists and is currently active
                cursor.execute("""
                    SELECT status, confidence_score FROM sites 
                    WHERE url = ? AND is_active = 1
                """, (url,))
                
                result = cursor.fetchone()
                if result:
                    current_status = result[0]
                    
                    if current_status == 'active':
                        # Move to quarantine on first failure
                        cursor.execute("""
                            UPDATE sites 
                            SET status = 'quarantined', last_verified = ?, is_active = 0
                            WHERE url = ?
                        """, (datetime.now(), url))
                        quarantined_count += 1
                        logger.info(f"Quarantined site: {url}")
                        
                    elif current_status == 'quarantined':
                        # TODO: Implement failure count tracking and eventual deactivation
                        # For now, just update timestamp
                        cursor.execute("""
                            UPDATE sites 
                            SET last_verified = ?
                            WHERE url = ?
                        """, (datetime.now(), url))
                        logger.info(f"Site remains quarantined: {url}")
            
            conn.commit()
            conn.close()
            
            return {'quarantined': quarantined_count, 'reactivated': 0}
            
        except Exception as e:
            logger.error(f"Failed to quarantine sites: {e}")
            return {'quarantined': 0, 'reactivated': 0}
    
    def run_discovery_cycle(self):
        """
        Execute a complete V2 discovery and verification cycle with quarantine management.
        
        Returns:
            dict: Summary of the discovery cycle results
        """
        logger.info("=" * 60)
        logger.info("SIGNAL SCOUT V2 - Starting Discovery Cycle")
        logger.info("=" * 60)
        
        cycle_start = time.time()
        
        # V2: Step 0: Re-verify quarantined sites first
        logger.info("Phase 0: Quarantine Re-verification")
        self._reverify_quarantined_sites()
        
        # Step 1: Discover URLs using V2 hunter modules with configuration
        logger.info("Phase 1: URL Discovery")
        operational_params = self.config.get('operational_parameters', {})
        serpapi_key = self.config.get('api_keys', {}).get('serpapi_key', None)
        
        discovered_urls = discover_urls(
            aggregator_urls=operational_params.get('aggregator_urls'),
            permutation_bases=operational_params.get('permutation_bases'), 
            permutation_tlds=operational_params.get('permutation_tlds'),
            serpapi_key=serpapi_key
        )
        logger.info(f"Discovered {len(discovered_urls)} candidate URLs")
        
        if not discovered_urls:
            logger.warning("No URLs discovered, ending cycle")
            return {
                'discovered': 0,
                'verified': 0,
                'failed': 0,
                'new_sites': 0,
                'updated_sites': 0,
                'quarantined': 0,
                'reactivated': 0,
                'duration': time.time() - cycle_start
            }
        
        # Step 2: Filter out existing URLs to focus on new discoveries
        existing_urls = self._get_existing_urls()
        new_urls = [url for url in discovered_urls if url not in existing_urls]
        existing_to_reverify = [url for url in discovered_urls if url in existing_urls]
        
        logger.info(f"New URLs to verify: {len(new_urls)}")
        logger.info(f"Existing URLs to re-verify: {len(existing_to_reverify)}")
        
        # Step 3: Verification phase with V2 dynamic verification
        logger.info("Phase 2: Verification Pipeline")
        
        verified_sites = []
        failed_sites = []
        new_sites = 0
        updated_sites = 0
        
        # Verify all URLs (prioritize new ones)
        all_urls_to_verify = new_urls + existing_to_reverify
        
        for i, url in enumerate(all_urls_to_verify, 1):
            logger.info(f"Verifying ({i}/{len(all_urls_to_verify)}): {url}")
            
            try:
                # V2: Pass browser instance to verification pipeline
                verification_result = verify_url(url, scout_instance=self)
                
                # V2: Use configurable threshold
                threshold = self.config.get('discovery_settings', {}).get('verification_confidence_threshold', 50)
                
                if verification_result['overall_confidence'] >= threshold:
                    verified_sites.append((url, verification_result))
                    
                    # Store in database
                    was_new = url in new_urls
                    self._store_verified_site(url, verification_result)
                    
                    if was_new:
                        new_sites += 1
                    else:
                        updated_sites += 1
                        
                else:
                    failed_sites.append(url)
                    logger.debug(f"Verification failed for {url} - confidence: {verification_result['overall_confidence']}")
                    
            except Exception as e:
                logger.error(f"Error verifying {url}: {e}")
                failed_sites.append(url)
        
        # Step 4: Cleanup - V2 quarantine failed sites
        logger.info("Phase 3: Database Maintenance")
        quarantine_stats = self._quarantine_failed_sites([url for url in failed_sites if url in existing_urls])
        
        # Step 5: Summary
        cycle_duration = time.time() - cycle_start
        
        summary = {
            'discovered': len(discovered_urls),
            'verified': len(verified_sites),
            'failed': len(failed_sites),
            'new_sites': new_sites,
            'updated_sites': updated_sites,
            'quarantined': quarantine_stats.get('quarantined', 0),
            'reactivated': quarantine_stats.get('reactivated', 0),
            'duration': cycle_duration
        }
        
        logger.info("=" * 60)
        logger.info("V2 DISCOVERY CYCLE COMPLETE")
        logger.info(f"Duration: {cycle_duration:.1f} seconds")
        logger.info(f"URLs Discovered: {summary['discovered']}")
        logger.info(f"Verification Results: {summary['verified']} passed, {summary['failed']} failed")
        logger.info(f"Database Changes: {summary['new_sites']} new sites, {summary['updated_sites']} updated")
        logger.info(f"Quarantine Actions: {summary['quarantined']} quarantined, {summary['reactivated']} reactivated")
        logger.info("=" * 60)
        
        return summary
    
    def _reverify_quarantined_sites(self):
        """
        V2 Feature: Re-verify quarantined sites to potentially reactivate them.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get quarantined sites
            cursor.execute("""
                SELECT url FROM sites 
                WHERE status = 'quarantined'
            """)
            
            quarantined_urls = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            if not quarantined_urls:
                logger.info("No quarantined sites to re-verify")
                return
                
            logger.info(f"Re-verifying {len(quarantined_urls)} quarantined sites")
            
            reactivated = 0
            threshold = self.config.get('discovery_settings', {}).get('verification_confidence_threshold', 50)
            
            for url in quarantined_urls:
                try:
                    verification_result = verify_url(url, scout_instance=self)
                    
                    if verification_result['overall_confidence'] >= threshold:
                        # Reactivate the site
                        self._reactivate_site(url, verification_result)
                        reactivated += 1
                        logger.info(f"Reactivated quarantined site: {url}")
                        
                except Exception as e:
                    logger.error(f"Error re-verifying quarantined site {url}: {e}")
            
            if reactivated > 0:
                logger.info(f"Reactivated {reactivated} sites from quarantine")
                
        except Exception as e:
            logger.error(f"Failed to re-verify quarantined sites: {e}")
    
    def _reactivate_site(self, url, verification_result):
        """
        V2 Feature: Reactivate a quarantined site that passed re-verification.
        
        Args:
            url (str): URL to reactivate
            verification_result (dict): Verification result
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            confidence_score = verification_result.get('overall_confidence', 0)
            timestamp = datetime.now()
            
            cursor.execute("""
                UPDATE sites 
                SET status = 'active', is_active = 1, confidence_score = ?, last_verified = ?
                WHERE url = ?
            """, (confidence_score, timestamp, url))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to reactivate site {url}: {e}")
    
    def get_database_status(self):
        """
        Get current status of the sites database with V2 metrics.
        
        Returns:
            dict: Database statistics including quarantine status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get counts
            cursor.execute("SELECT COUNT(*) FROM sites")
            total_sites = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sites WHERE is_active = 1")
            active_sites = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sites WHERE source = 'scout_discovery'")
            scout_discovered = cursor.fetchone()[0]
            
            # V2: Status-based counts
            cursor.execute("SELECT COUNT(*) FROM sites WHERE status = 'active'")
            status_active = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sites WHERE status = 'quarantined'")
            quarantined_sites = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sites WHERE status = 'inactive'")
            inactive_sites = cursor.fetchone()[0]
            
            # V2: Average confidence score
            cursor.execute("SELECT AVG(confidence_score) FROM sites WHERE is_active = 1")
            avg_confidence = cursor.fetchone()[0] or 0
            
            # V2: High-confidence sites (>= 70)
            cursor.execute("SELECT COUNT(*) FROM sites WHERE confidence_score >= 70")
            high_confidence_sites = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT MAX(last_verified) FROM sites 
                WHERE last_verified IS NOT NULL
            """)
            last_activity = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_sites': total_sites,
                'active_sites': active_sites,
                'scout_discovered': scout_discovered,
                'status_active': status_active,
                'quarantined_sites': quarantined_sites,
                'inactive_sites': inactive_sites,
                'avg_confidence': round(avg_confidence, 1),
                'high_confidence_sites': high_confidence_sites,
                'last_activity': last_activity
            }
            
        except Exception as e:
            logger.error(f"Failed to get database status: {e}")
            return {}


def main():
    """
    Main execution function for standalone script usage.
    """
    try:
        scout = SignalScout()
        
        # Display initial database status
        status = scout.get_database_status()
        logger.info(f"Initial database status: {status}")
        
        # Run discovery cycle
        summary = scout.run_discovery_cycle()
        
        # Display final database status
        final_status = scout.get_database_status()
        logger.info(f"Final database status: {final_status}")
        
        return summary
        
    except KeyboardInterrupt:
        logger.info("Discovery cycle interrupted by user")
    except Exception as e:
        logger.error(f"Scout execution failed: {e}")
        raise


if __name__ == "__main__":
    main()