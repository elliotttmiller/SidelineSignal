"""
SidelineSignal V5.0 ReportingAgent - After-Action Analysis and Structured Reporting

This module implements the ReportingAgent, which analyzes mission results and generates
structured JSON reports for the next planning cycle, closing the cognitive feedback loop.
"""

import json
import logging
import os
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportingAgent:
    """
    The ReportingAgent analyzes mission results and creates structured reports.
    
    It provides the critical feedback loop by:
    1. Analyzing log data for mission performance metrics
    2. Examining database changes to quantify discoveries
    3. Identifying successful and failed operations
    4. Creating structured JSON reports for the PlannerAgent
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the ReportingAgent.
        
        Args:
            project_root: Root directory of the SidelineSignal project
        """
        if project_root is None:
            project_root = str(Path(__file__).parent.parent.absolute())
        
        self.project_root = Path(project_root)
        self.log_file = self.project_root / "signal_scout" / "scout.log"
        self.db_path = self.project_root / "shared_data" / "sites.db"
        
        logger.info(f"ReportingAgent initialized with project root: {self.project_root}")
    
    def generate_after_action_report(self, log_data: Optional[str] = None, 
                                   db_changes: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive after-action report from mission results.
        
        Args:
            log_data: Raw log data from the mission (if None, reads from log file)
            db_changes: Database change information (if None, analyzes current DB)
            
        Returns:
            Structured JSON report for consumption by PlannerAgent
        """
        logger.info("ReportingAgent generating after-action report...")
        
        # Get log data
        if log_data is None:
            log_data = self._read_log_data()
        
        # Analyze mission performance
        performance_metrics = self._analyze_performance(log_data)
        
        # Analyze database changes
        db_analysis = self._analyze_database_changes()
        
        # Identify effective and failed operations
        operational_analysis = self._analyze_operations(log_data)
        
        # Generate comprehensive report
        report = {
            "report_type": "after_action",
            "timestamp": datetime.now().isoformat(),
            "mission_summary": {
                "duration_minutes": performance_metrics.get("duration_minutes", 0),
                "pages_crawled": performance_metrics.get("pages_crawled", 0),
                "links_evaluated": performance_metrics.get("links_evaluated", 0)
            },
            "discovery_results": {
                "new_sites_found": db_analysis.get("new_sites_count", 0),
                "sites_quarantined": db_analysis.get("quarantined_count", 0),
                "total_active_sites": db_analysis.get("active_sites_count", 0),
                "database_status": db_analysis.get("status", "unknown")
            },
            "performance_analysis": {
                "ai_classification_rate": performance_metrics.get("ai_success_rate", 0),
                "verification_success_rate": performance_metrics.get("verification_success_rate", 0),
                "most_effective_hunt_method": operational_analysis.get("most_effective_method", "unknown"),
                "avg_sites_per_query": operational_analysis.get("avg_sites_per_query", 0)
            },
            "failed_operations": operational_analysis.get("failed_operations", []),
            "successful_patterns": operational_analysis.get("successful_patterns", []),
            "recommendations": self._generate_recommendations(performance_metrics, db_analysis, operational_analysis),
            "raw_metrics": {
                "log_analysis": performance_metrics,
                "db_analysis": db_analysis,
                "operational_analysis": operational_analysis
            }
        }
        
        logger.info("ReportingAgent completed after-action report generation")
        return report
    
    def _read_log_data(self) -> str:
        """Read the scout log file for analysis."""
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"Read {len(content)} characters from scout log")
                return content
            else:
                logger.warning("Scout log file not found")
                return ""
        except Exception as e:
            logger.error(f"Failed to read scout log: {e}")
            return ""
    
    def _analyze_performance(self, log_data: str) -> Dict[str, Any]:
        """Analyze performance metrics from log data."""
        metrics = {}
        
        try:
            # Count key operational events
            metrics["pages_crawled"] = log_data.count("New page being crawled")
            metrics["links_evaluated"] = log_data.count("Link being evaluated")
            metrics["ai_classifications"] = log_data.count("classifier's verdict")
            metrics["ai_positive"] = log_data.count("(POSITIVE)")
            metrics["ai_negative"] = log_data.count("(NEGATIVE)")
            metrics["v2_verifications"] = log_data.count("V2 verification")
            metrics["v2_successes"] = log_data.count("successfully written to database")
            
            # Calculate rates
            if metrics["ai_classifications"] > 0:
                metrics["ai_success_rate"] = metrics["ai_positive"] / metrics["ai_classifications"]
            else:
                metrics["ai_success_rate"] = 0
                
            if metrics["v2_verifications"] > 0:
                metrics["verification_success_rate"] = metrics["v2_successes"] / metrics["v2_verifications"]
            else:
                metrics["verification_success_rate"] = 0
            
            # Estimate mission duration from logs
            lines = log_data.split('\n')
            timestamps = []
            for line in lines:
                if '[' in line and ']' in line:
                    try:
                        timestamp_str = line.split('[')[1].split(']')[0]
                        # This is a simplified timestamp parsing - may need adjustment
                        timestamps.append(timestamp_str)
                    except:
                        continue
            
            if len(timestamps) >= 2:
                # Rough duration estimate (would need proper timestamp parsing for accuracy)
                metrics["duration_minutes"] = 5  # Default estimate
            else:
                metrics["duration_minutes"] = 0
            
            logger.info(f"Performance analysis: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            return {}
    
    def _analyze_database_changes(self) -> Dict[str, Any]:
        """Analyze changes in the database to quantify discoveries."""
        analysis = {}
        
        try:
            if not self.db_path.exists():
                logger.warning("Database file not found for analysis")
                return {"status": "database_not_found", "new_sites_count": 0, 
                       "active_sites_count": 0, "quarantined_count": 0}
            
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Count total sites
                cursor.execute("SELECT COUNT(*) FROM sites")
                total_sites = cursor.fetchone()[0]
                analysis["total_sites_count"] = total_sites
                
                # Count active sites
                cursor.execute("SELECT COUNT(*) FROM sites WHERE is_active = 1")
                active_sites = cursor.fetchone()[0]
                analysis["active_sites_count"] = active_sites
                
                # Count recently added sites (rough estimate)
                cursor.execute("""
                    SELECT COUNT(*) FROM sites 
                    WHERE datetime(last_verified) >= datetime('now', '-1 hour')
                """)
                recent_sites = cursor.fetchone()[0]
                analysis["new_sites_count"] = recent_sites
                
                # Count quarantined/inactive sites
                cursor.execute("SELECT COUNT(*) FROM sites WHERE is_active = 0")
                quarantined = cursor.fetchone()[0]
                analysis["quarantined_count"] = quarantined
                
                # Get source breakdown
                cursor.execute("""
                    SELECT source, COUNT(*) as count 
                    FROM sites 
                    GROUP BY source 
                    ORDER BY count DESC
                """)
                source_breakdown = cursor.fetchall()
                analysis["source_breakdown"] = dict(source_breakdown)
                
                analysis["status"] = "analysis_complete"
                
            logger.info(f"Database analysis: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"Database analysis failed: {e}")
            return {"status": "analysis_failed", "error": str(e)}
    
    def _analyze_operations(self, log_data: str) -> Dict[str, Any]:
        """Analyze operational patterns to identify successes and failures."""
        analysis = {}
        
        try:
            # Extract failed operations
            failed_operations = []
            lines = log_data.split('\n')
            
            for line in lines:
                if '[ERROR]' in line or 'failed' in line.lower() or 'timeout' in line.lower():
                    # Clean and add error info
                    clean_line = line.strip()
                    if len(clean_line) > 20:  # Avoid empty or too short lines
                        failed_operations.append(clean_line[-200:])  # Last 200 chars
            
            analysis["failed_operations"] = failed_operations[:10]  # Limit to 10 most recent
            
            # Identify successful patterns
            successful_patterns = []
            
            # Look for successful seed queries or methods
            for line in lines:
                if "successfully written to database" in line and "https://" in line:
                    # Extract successful discovery patterns
                    if "streameast" in line.lower():
                        successful_patterns.append("streameast_domain_pattern")
                    if "sport" in line.lower():
                        successful_patterns.append("sports_keyword_success")
                    if "live" in line.lower():
                        successful_patterns.append("live_streaming_pattern")
            
            # Remove duplicates and limit
            analysis["successful_patterns"] = list(set(successful_patterns))[:5]
            
            # Determine most effective method
            v2_successes = log_data.count("V2 verification")
            genesis_mentions = log_data.count("genesis")
            aggregator_mentions = log_data.count("aggregator")
            
            if v2_successes > 5:
                analysis["most_effective_method"] = "v2_verification_pipeline"
            elif genesis_mentions > aggregator_mentions:
                analysis["most_effective_method"] = "genesis_seed_discovery"
            else:
                analysis["most_effective_method"] = "community_aggregator"
            
            # Calculate average sites per query (rough estimate)
            ai_positives = log_data.count("(POSITIVE)")
            seed_queries = log_data.count("seed_queries") or 5  # Default estimate
            analysis["avg_sites_per_query"] = ai_positives / max(seed_queries, 1)
            
            logger.info(f"Operations analysis: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"Operations analysis failed: {e}")
            return {"failed_operations": [], "successful_patterns": [], 
                   "most_effective_method": "unknown", "avg_sites_per_query": 0}
    
    def _generate_recommendations(self, performance_metrics: Dict, db_analysis: Dict, 
                                operational_analysis: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        try:
            # Performance-based recommendations
            ai_success_rate = performance_metrics.get("ai_success_rate", 0)
            if ai_success_rate < 0.1:
                recommendations.append("AI classification success rate is low - consider retraining model")
            elif ai_success_rate > 0.8:
                recommendations.append("AI classification performing excellently - maintain current approach")
            
            # Discovery-based recommendations
            new_sites = db_analysis.get("new_sites_count", 0)
            if new_sites == 0:
                recommendations.append("No new sites discovered - pivot to different search strategies")
            elif new_sites > 10:
                recommendations.append("High discovery rate - double down on current successful patterns")
            
            # Method-based recommendations
            most_effective = operational_analysis.get("most_effective_method", "")
            if most_effective == "genesis_seed_discovery":
                recommendations.append("Genesis seed discovery most effective - expand seed query diversity")
            elif most_effective == "community_aggregator":
                recommendations.append("Community aggregation working well - target more curated sources")
            
            # Failure analysis recommendations
            failed_ops = len(operational_analysis.get("failed_operations", []))
            if failed_ops > 5:
                recommendations.append("High failure rate detected - review error patterns and improve error handling")
            
            # Ensure we have at least one recommendation
            if not recommendations:
                recommendations.append("Continue current strategy and monitor for patterns")
            
            return recommendations[:5]  # Limit to 5 key recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Analysis incomplete - manual review recommended"]
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Save the after-action report to disk.
        
        Args:
            report: The generated report
            filename: Custom filename (if None, generates timestamp-based name)
            
        Returns:
            Path to saved report file
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"after_action_report_{timestamp}.json"
            
            reports_dir = self.project_root / "shared_data" / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            report_path = reports_dir / filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"After-action report saved to: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return ""
    
    def get_latest_report(self) -> Optional[Dict[str, Any]]:
        """
        Load the most recent after-action report.
        
        Returns:
            Latest report dictionary or None if no reports exist
        """
        try:
            reports_dir = self.project_root / "shared_data" / "reports"
            if not reports_dir.exists():
                return None
            
            # Find most recent report file
            report_files = list(reports_dir.glob("after_action_report_*.json"))
            if not report_files:
                return None
            
            latest_file = max(report_files, key=lambda p: p.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            logger.info(f"Loaded latest report from: {latest_file}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to load latest report: {e}")
            return None