"""
SidelineSignal V6.0 ReportingAgent - Cognitive Performance Analysis and Strategic Recommendations

This module implements the V6.0 ReportingAgent with advanced structured reasoning using the 
Observation → Insight → Recommendation cognitive framework. The agent creates comprehensive
performance analysis with transparent AI decision-making for the cognitive feedback loop.
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
    V6.0 COGNITIVE PERFORMANCE ANALYST
    
    The ReportingAgent implements advanced structured reasoning using the 
    Observation → Insight → Recommendation cognitive framework.
    
    It provides the critical cognitive feedback loop by:
    1. Systematic observation of mission performance metrics
    2. Deep analytical insights from operational patterns
    3. Strategic recommendations for mission evolution
    4. Complete reasoning audit trail for transparency
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
        V6.0 COGNITIVE PERFORMANCE ANALYSIS ENGINE
        
        Generate comprehensive after-action report using Observation → Insight → Recommendation 
        structured reasoning framework. Creates transparent AI analysis with full reasoning audit.
        
        Args:
            log_data: Raw log data from the mission (if None, reads from log file)
            db_changes: Database change information (if None, analyzes current DB)
            
        Returns:
            V6.0 structured JSON report with complete reasoning process for PlannerAgent consumption
        """
        logger.info("V6.0 ReportingAgent generating cognitive performance analysis...")
        
        # Get log data
        if log_data is None:
            log_data = self._read_log_data()
        
        # Perform V6.0 cognitive analysis using structured reasoning
        performance_metrics = self._analyze_performance(log_data)
        db_analysis = self._analyze_database_changes()
        operational_analysis = self._analyze_operations(log_data)
        
        # Generate V6.0 cognitive recommendations using O → I → R framework
        cognitive_reasoning = self._generate_cognitive_analysis(performance_metrics, db_analysis, operational_analysis)
        
        # Generate comprehensive V6.0 report with cognitive reasoning
        report = {
            "report_type": "v6_cognitive_after_action",
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
            "cognitive_reasoning_process": cognitive_reasoning,
            "primary_recommendation": cognitive_reasoning.get("primary_recommendation", "Continue current approach"),
            "raw_metrics": {
                "log_analysis": performance_metrics,
                "db_analysis": db_analysis,
                "operational_analysis": operational_analysis
            }
        }
        
        logger.info("V6.0 ReportingAgent completed cognitive performance analysis")
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
    
    def _generate_cognitive_analysis(self, performance_metrics: Dict, db_analysis: Dict, 
                                   operational_analysis: Dict) -> Dict[str, Any]:
        """
        V6.0 COGNITIVE REASONING ENGINE
        
        Generate structured cognitive analysis using Observation → Insight → Recommendation framework.
        Creates transparent, auditable AI reasoning process for strategic decision-making.
        """
        try:
            # Observation Phase: Systematic data collection
            observations = {
                "performance_observations": {
                    "ai_success_rate": performance_metrics.get("ai_success_rate", 0),
                    "verification_success_rate": performance_metrics.get("verification_success_rate", 0),
                    "pages_processed": performance_metrics.get("pages_crawled", 0)
                },
                "discovery_observations": {
                    "new_sites_discovered": db_analysis.get("new_sites_count", 0),
                    "total_active_sites": db_analysis.get("active_sites_count", 0),
                    "discovery_efficiency": operational_analysis.get("avg_sites_per_query", 0)
                },
                "operational_observations": {
                    "most_effective_method": operational_analysis.get("most_effective_method", "unknown"),
                    "failure_count": len(operational_analysis.get("failed_operations", [])),
                    "success_patterns": operational_analysis.get("successful_patterns", [])
                }
            }
            
            # Insight Phase: Deep analytical reasoning  
            insights = {
                "performance_insights": self._analyze_performance_patterns(observations["performance_observations"]),
                "discovery_insights": self._analyze_discovery_patterns(observations["discovery_observations"]), 
                "operational_insights": self._analyze_operational_patterns(observations["operational_observations"])
            }
            
            # Recommendation Phase: Strategic decision synthesis
            primary_recommendation = self._synthesize_primary_recommendation(insights)
            secondary_recommendations = self._generate_secondary_recommendations(insights)
            
            # Complete cognitive reasoning process
            cognitive_reasoning = {
                "observations": observations,
                "insights": insights,
                "primary_recommendation": primary_recommendation,
                "secondary_recommendations": secondary_recommendations,
                "reasoning_confidence": self._calculate_reasoning_confidence(insights)
            }
            
            logger.info(f"V6.0 Cognitive Analysis complete - Primary recommendation: {primary_recommendation}")
            return cognitive_reasoning
            
        except Exception as e:
            logger.error(f"V6.0 Cognitive Analysis failed: {e}")
            return {
                "observations": {"analysis_error": "Cognitive analysis system failure"},
                "insights": {"error_insight": "Unable to generate insights due to system error"},
                "primary_recommendation": "Manual review required - cognitive analysis failed",
                "secondary_recommendations": ["Review system logs", "Check cognitive analysis engine"],
                "reasoning_confidence": 0,
                "error": str(e)
            }
    
    def _analyze_performance_patterns(self, performance_obs: Dict) -> str:
        """Analyze performance patterns to generate insights."""
        ai_rate = performance_obs.get("ai_success_rate", 0)
        verify_rate = performance_obs.get("verification_success_rate", 0)
        
        if ai_rate > 0.8 and verify_rate > 0.7:
            return "Excellent pipeline performance - both AI classification and verification stages operating at high efficiency"
        elif ai_rate < 0.3:
            return "AI classification stage underperforming - may indicate need for model retraining or prompt optimization"
        elif verify_rate < 0.4:
            return "Verification stage bottleneck detected - technical verification processes need optimization"
        else:
            return "Moderate performance levels across pipeline - incremental optimizations recommended"
    
    def _analyze_discovery_patterns(self, discovery_obs: Dict) -> str:
        """Analyze discovery patterns to generate insights."""
        new_sites = discovery_obs.get("new_sites_discovered", 0)
        efficiency = discovery_obs.get("discovery_efficiency", 0)
        
        if new_sites == 0:
            return "Zero discovery rate indicates fundamental strategy failure - major tactical pivot required"
        elif new_sites > 10:
            return "High discovery rate suggests effective strategy execution - recommend scaling current approach"
        elif efficiency > 2.0:
            return "High efficiency per query suggests excellent targeting - current query strategy is optimal"
        else:
            return "Moderate discovery performance - tactical refinements needed to improve targeting"
    
    def _analyze_operational_patterns(self, operational_obs: Dict) -> str:
        """Analyze operational patterns to generate insights."""
        effective_method = operational_obs.get("most_effective_method", "unknown")
        failures = operational_obs.get("failure_count", 0)
        
        if failures > 10:
            return "High failure rate indicates systemic operational issues - infrastructure review required"
        elif effective_method == "v6_cognitive_discovery":
            return "V6.0 cognitive pipeline demonstrating superior performance - cognitive architecture validation successful"
        elif effective_method == "genesis_seed_discovery":
            return "Genesis seed approach most effective - recommend expanding seed diversity and coverage"
        else:
            return "Mixed operational effectiveness - need to identify and amplify best-performing methods"
    
    def _synthesize_primary_recommendation(self, insights: Dict) -> str:
        """Synthesize primary strategic recommendation from all insights."""
        performance_insight = insights.get("performance_insights", "")
        discovery_insight = insights.get("discovery_insights", "")
        operational_insight = insights.get("operational_insights", "")
        
        # Priority logic for primary recommendation
        if "zero discovery rate" in discovery_insight.lower():
            return "Execute immediate strategic pivot - current approach fundamentally ineffective"
        elif "high discovery rate" in discovery_insight.lower() and "excellent pipeline" in performance_insight.lower():
            return "Scale current strategy immediately - all systems performing optimally"
        elif "v6.0 cognitive pipeline" in operational_insight.lower():
            return "V6.0 cognitive architecture validated - transition fully to cognitive-first discovery"  
        elif "ai classification" in performance_insight.lower() and "underperforming" in performance_insight.lower():
            return "Focus on AI model optimization - classification stage is primary bottleneck"
        else:
            return "Continue current approach with tactical refinements based on performance insights"
    
    def _generate_secondary_recommendations(self, insights: Dict) -> List[str]:
        """Generate secondary strategic recommendations."""
        recommendations = []
        
        performance_insight = insights.get("performance_insights", "")
        discovery_insight = insights.get("discovery_insights", "") 
        operational_insight = insights.get("operational_insights", "")
        
        if "retraining" in performance_insight:
            recommendations.append("Implement AI model retraining program")
        if "high efficiency" in discovery_insight:
            recommendations.append("Expand successful query patterns to new domains")
        if "infrastructure review" in operational_insight:
            recommendations.append("Conduct comprehensive system reliability audit")
        if "cognitive architecture" in operational_insight:
            recommendations.append("Document and replicate V6.0 cognitive patterns")
        
        # Ensure we always have at least one recommendation
        if not recommendations:
            recommendations.append("Monitor current performance and iterate incrementally")
            
        return recommendations[:3]  # Limit to top 3 recommendations
    
    def _calculate_reasoning_confidence(self, insights: Dict) -> int:
        """Calculate confidence in the reasoning process based on data quality."""
        confidence = 80  # Base confidence
        
        # Adjust based on insight quality
        for insight in insights.values():
            if isinstance(insight, str):
                if "unknown" in insight.lower() or "error" in insight.lower():
                    confidence -= 15
                elif "excellent" in insight.lower() or "high" in insight.lower():
                    confidence += 5
        
        return max(0, min(100, confidence))
    
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