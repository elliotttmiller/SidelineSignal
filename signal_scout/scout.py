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
        
        logger.info(f"Signal Scout initialized with database: {self.db_path}")
        logger.info(f"Configuration loaded from: {self.config_path}")
        
        # Ensure database exists and has correct schema
        self._ensure_database()
    
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
                        is_active BOOLEAN
                    )
                ''')
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
            
            # Try to update existing entry first
            cursor.execute("""
                UPDATE sites 
                SET last_verified = ?, confidence_score = ?, is_active = ?
                WHERE url = ?
            """, (timestamp, confidence_score, True, url))
            
            if cursor.rowcount == 0:
                # Insert new entry
                cursor.execute("""
                    INSERT INTO sites (name, url, source, last_verified, confidence_score, is_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (site_name, url, 'scout_discovery', timestamp, confidence_score, True))
                logger.info(f"Added new site: {site_name} ({url}) - confidence: {confidence_score}")
            else:
                logger.info(f"Updated existing site: {site_name} ({url}) - confidence: {confidence_score}")
                
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store site {url}: {e}")
    
    def _deactivate_failed_sites(self, failed_urls):
        """
        Mark sites as inactive if they repeatedly fail verification.
        
        Args:
            failed_urls (list): List of URLs that failed verification
        """
        if not failed_urls:
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get sites that were last verified more than 24 hours ago and failed again
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for url in failed_urls:
                cursor.execute("""
                    SELECT last_verified FROM sites 
                    WHERE url = ? AND is_active = 1
                """, (url,))
                
                result = cursor.fetchone()
                if result:
                    last_verified = datetime.fromisoformat(result[0])
                    if last_verified < cutoff_time:
                        cursor.execute("""
                            UPDATE sites 
                            SET is_active = 0, last_verified = ?
                            WHERE url = ?
                        """, (datetime.now(), url))
                        logger.info(f"Deactivated failing site: {url}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to deactivate sites: {e}")
    
    def run_discovery_cycle(self):
        """
        Execute a complete discovery and verification cycle.
        
        Returns:
            dict: Summary of the discovery cycle results
        """
        logger.info("=" * 60)
        logger.info("SIGNAL SCOUT - Starting Discovery Cycle")
        logger.info("=" * 60)
        
        cycle_start = time.time()
        
        # Step 1: Discover URLs using hunter modules with configuration
        logger.info("Phase 1: URL Discovery")
        operational_params = self.config.get('operational_parameters', {})
        discovered_urls = discover_urls(
            aggregator_urls=operational_params.get('aggregator_urls'),
            permutation_bases=operational_params.get('permutation_bases'), 
            permutation_tlds=operational_params.get('permutation_tlds')
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
                'duration': time.time() - cycle_start
            }
        
        # Step 2: Filter out existing URLs to focus on new discoveries
        existing_urls = self._get_existing_urls()
        new_urls = [url for url in discovered_urls if url not in existing_urls]
        existing_to_reverify = [url for url in discovered_urls if url in existing_urls]
        
        logger.info(f"New URLs to verify: {len(new_urls)}")
        logger.info(f"Existing URLs to re-verify: {len(existing_to_reverify)}")
        
        # Step 3: Verification phase
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
                verification_result = verify_url(url)
                
                if verification_result['passed']:
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
                    logger.debug(f"Verification failed for {url}")
                    
            except Exception as e:
                logger.error(f"Error verifying {url}: {e}")
                failed_sites.append(url)
        
        # Step 4: Cleanup - deactivate persistently failing sites
        logger.info("Phase 3: Database Maintenance")
        self._deactivate_failed_sites([url for url in failed_sites if url in existing_urls])
        
        # Step 5: Summary
        cycle_duration = time.time() - cycle_start
        
        summary = {
            'discovered': len(discovered_urls),
            'verified': len(verified_sites),
            'failed': len(failed_sites),
            'new_sites': new_sites,
            'updated_sites': updated_sites,
            'duration': cycle_duration
        }
        
        logger.info("=" * 60)
        logger.info("DISCOVERY CYCLE COMPLETE")
        logger.info(f"Duration: {cycle_duration:.1f} seconds")
        logger.info(f"URLs Discovered: {summary['discovered']}")
        logger.info(f"Verification Results: {summary['verified']} passed, {summary['failed']} failed")
        logger.info(f"Database Changes: {summary['new_sites']} new sites, {summary['updated_sites']} updated")
        logger.info("=" * 60)
        
        return summary
    
    def get_database_status(self):
        """
        Get current status of the sites database.
        
        Returns:
            dict: Database statistics
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