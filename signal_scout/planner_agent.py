"""
SidelineSignal V5.0 PlannerAgent - Autonomous Mission Strategy Generator

This module implements the PlannerAgent, the cognitive core of the SidelineSignal V5.0 
Cognitive Organism. It autonomously generates mission strategies and adapts based on 
previous mission reports, creating a truly self-minded discovery system.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from openai import OpenAI

logger = logging.getLogger(__name__)


class PlannerAgent:
    """
    The PlannerAgent is the strategic mind of the SidelineSignal V5.0 Cognitive Organism.
    
    It generates autonomous mission plans by:
    1. Genesis Run: Starting with a foundational objective and generating initial strategy
    2. Adaptive Runs: Analyzing previous mission reports to evolve strategy
    3. Self-Correction: Learning from successes and failures to improve performance
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the PlannerAgent with LLM configuration.
        
        Args:
            config_path: Path to llm_config.json file
        """
        self.config = self._load_config(config_path)
        self.client = None
        self._initialize_client()
        
        # Genesis objective - the foundational mission that drives all strategy
        self.genesis_objective = (
            "Your mission is to discover and maintain a database of active sports streaming websites. "
            "Focus on finding reliable, functional streaming sites that provide live sports content."
        )
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load LLM configuration from JSON file."""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'llm_config.json')
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"PlannerAgent configuration loaded from: {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load PlannerAgent configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if config file fails to load."""
        return {
            "llm_settings": {
                "api_url": "http://localhost:1234/v1",
                "model_name": "local-model",
                "api_key": "lm-studio",
                "max_tokens": 1000,
                "temperature": 0.3,
                "timeout": 60
            }
        }
    
    def _initialize_client(self):
        """Initialize the OpenAI client for LLM communication."""
        try:
            self.client = OpenAI(
                base_url=self.config["llm_settings"]["api_url"],
                api_key=self.config["llm_settings"]["api_key"]
            )
            logger.info("PlannerAgent LLM client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PlannerAgent LLM client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if the LLM is available for planning."""
        if not self.client:
            return False
        
        try:
            # Quick test call
            response = self.client.completions.create(
                model=self.config["llm_settings"]["model_name"],
                prompt="Test",
                max_tokens=1,
                timeout=5
            )
            return True
        except Exception:
            return False
    
    def generate_mission_plan(self, previous_report: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate an autonomous mission plan.
        
        Args:
            previous_report: Structured report from the previous mission (None for genesis run)
            
        Returns:
            Dict containing the mission plan with seed_queries and strategy
        """
        logger.info("PlannerAgent generating mission plan...")
        
        if previous_report is None:
            # Genesis run - create initial strategy
            return self._generate_genesis_plan()
        else:
            # Adaptive run - learn from previous results
            return self._generate_adaptive_plan(previous_report)
    
    def _generate_genesis_plan(self) -> Dict[str, Any]:
        """
        V6.0 GENESIS COGNITIVE PLANNER
        
        Generate the initial strategic mission plan using structured reasoning framework.
        Implements Status Review → Strategic Goal → Tactical Execution thought process.
        """
        logger.info("V6.0 PlannerAgent executing GENESIS COGNITIVE PLANNING - creating strategic mission")
        
        if not self.client or not self.is_available():
            logger.warning("LLM not available - using V6.0 fallback genesis plan")
            return self._get_v6_fallback_genesis_plan()
        
        genesis_prompt = f"""
You are a world-class autonomous strategic AI planner for a sports streaming discovery mission. 

Use this STRATEGIC REASONING FRAMEWORK:

1. <Status_Review>: Assess the current situation and mission context
2. <Strategic_Goal>: Define the primary objective and success metrics  
3. <Tactical_Execution_Plan>: Design specific actions and query strategy

Your mission: {self.genesis_objective}

Respond with ONLY a valid JSON object containing your complete strategic reasoning:

{{
    "mission_type": "genesis_cognitive",
    "timestamp": "{datetime.now().isoformat()}",
    "strategic_reasoning_process": {{
        "status_review": "Your assessment of the current mission context and starting conditions",
        "strategic_goal": "Your definition of mission success and key objectives", 
        "tactical_execution_plan": "Your specific approach for discovering sports streaming sites"
    }},
    "seed_queries": ["query1", "query2", "query3", "query4", "query5"],
    "confidence_assessment": "Your confidence in this strategic approach and why",
    "success_metrics": ["metric1", "metric2", "metric3"]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config["llm_settings"]["model_name"],
                messages=[
                    {"role": "system", "content": "You are an expert autonomous strategic planning AI with advanced reasoning capabilities."},
                    {"role": "user", "content": genesis_prompt}
                ],
                max_tokens=self.config["llm_settings"]["max_tokens"],
                temperature=self.config["llm_settings"]["temperature"],
                timeout=self.config["llm_settings"]["timeout"]
            )
            
            plan_text = response.choices[0].message.content.strip()
            logger.info(f"V6.0 PlannerAgent received strategic reasoning response: {plan_text[:150]}...")
            
            # Parse V6.0 structured reasoning JSON
            plan = json.loads(plan_text)
            
            # Validate V6.0 required fields
            required_fields = ["strategic_reasoning_process", "seed_queries", "confidence_assessment"]
            for field in required_fields:
                if field not in plan:
                    raise ValueError(f"Missing required V6.0 field: {field}")
            
            # Validate reasoning process structure
            reasoning_fields = ["status_review", "strategic_goal", "tactical_execution_plan"]
            reasoning_process = plan.get("strategic_reasoning_process", {})
            for field in reasoning_fields:
                if field not in reasoning_process:
                    reasoning_process[field] = f"Missing {field} - fallback reasoning applied"
            
            logger.info("V6.0 PlannerAgent generated strategic cognitive plan successfully")
            return plan
            
        except Exception as e:
            logger.error(f"V6.0 PlannerAgent strategic cognitive planning failed: {e}")
            return self._get_v6_fallback_genesis_plan()
    
    def _generate_adaptive_plan(self, previous_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        V6.0 ADAPTIVE COGNITIVE PLANNER
        
        Generate adaptive strategic plan using structured reasoning based on previous results.
        Implements advanced Status Review → Strategic Goal → Tactical Execution framework.
        """
        logger.info("V6.0 PlannerAgent executing ADAPTIVE COGNITIVE PLANNING - analyzing previous results")
        
        if not self.client or not self.is_available():
            logger.warning("LLM not available - using V6.0 fallback adaptive plan")
            return self._get_v6_fallback_adaptive_plan(previous_report)
        
        adaptive_prompt = f"""
You are a world-class autonomous strategic AI planner analyzing mission results for strategic evolution.

Previous mission report:
{json.dumps(previous_report, indent=2)}

Use this STRATEGIC REASONING FRAMEWORK:

1. <Status_Review>: Analyze the previous mission results and current situation
2. <Strategic_Goal>: Evolve the mission objectives based on what was learned
3. <Tactical_Execution_Plan>: Design improved tactics incorporating lessons learned

Respond with ONLY a valid JSON object containing your complete strategic reasoning:

{{
    "mission_type": "adaptive_cognitive",
    "timestamp": "{datetime.now().isoformat()}",
    "strategic_reasoning_process": {{
        "status_review": "Your analysis of previous results and current strategic position",
        "strategic_goal": "Your evolved mission objectives based on learning",
        "tactical_execution_plan": "Your improved tactical approach incorporating lessons learned"
    }},
    "seed_queries": ["evolved_query1", "evolved_query2", "evolved_query3", "evolved_query4", "evolved_query5"],
    "confidence_assessment": "Your confidence in this evolved strategy and justification",
    "adaptations_made": "Specific strategic changes made based on previous mission analysis",
    "expected_improvements": ["improvement1", "improvement2", "improvement3"]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config["llm_settings"]["model_name"],
                messages=[
                    {"role": "system", "content": "You are an expert autonomous strategic AI that evolves strategy based on mission results and analysis."},
                    {"role": "user", "content": adaptive_prompt}
                ],
                max_tokens=self.config["llm_settings"]["max_tokens"],
                temperature=self.config["llm_settings"]["temperature"],
                timeout=self.config["llm_settings"]["timeout"]
            )
            
            plan_text = response.choices[0].message.content.strip()
            logger.info(f"V6.0 PlannerAgent received adaptive strategic reasoning: {plan_text[:150]}...")
            
            # Parse V6.0 structured reasoning JSON
            plan = json.loads(plan_text)
            
            # Validate V6.0 required fields
            required_fields = ["strategic_reasoning_process", "seed_queries", "adaptations_made"]
            for field in required_fields:
                if field not in plan:
                    raise ValueError(f"Missing required V6.0 adaptive field: {field}")
            
            # Validate reasoning process structure
            reasoning_fields = ["status_review", "strategic_goal", "tactical_execution_plan"]
            reasoning_process = plan.get("strategic_reasoning_process", {})
            for field in reasoning_fields:
                if field not in reasoning_process:
                    reasoning_process[field] = f"Missing {field} - fallback reasoning applied"
            
            logger.info("V6.0 PlannerAgent generated adaptive cognitive plan successfully")
            return plan
            
        except Exception as e:
            logger.error(f"V6.0 PlannerAgent adaptive cognitive planning failed: {e}")
            return self._get_v6_fallback_adaptive_plan(previous_report)
    
    def _get_v6_fallback_genesis_plan(self) -> Dict[str, Any]:
        """V6.0 fallback genesis plan with structured reasoning when LLM is unavailable."""
        return {
            "mission_type": "genesis_cognitive_fallback",
            "timestamp": datetime.now().isoformat(),
            "strategic_reasoning_process": {
                "status_review": "Starting mission with no prior data. Operating in LLM fallback mode due to unavailability of strategic reasoning engine.",
                "strategic_goal": "Discover active sports streaming websites using proven query patterns targeting major sports and community-driven discovery approaches.",
                "tactical_execution_plan": "Deploy multi-angle approach covering direct sport searches, community platforms, and streaming-focused terms to maximize discovery probability."
            },
            "seed_queries": [
                "watch NFL live free streaming",
                "soccer stream free online", 
                "NBA live stream reddit",
                "MLB streaming sites free",
                "live sports streaming free"
            ],
            "confidence_assessment": "Medium confidence in fallback strategy based on historical effectiveness of these query patterns",
            "success_metrics": ["sites_discovered", "verification_rate", "streaming_site_ratio"]
        }
    
    def _get_v6_fallback_adaptive_plan(self, previous_report: Dict[str, Any]) -> Dict[str, Any]:
        """V6.0 fallback adaptive plan with structured reasoning when LLM is unavailable."""
        # Simple adaptive logic based on previous results
        new_sites = previous_report.get("discovery_results", {}).get("new_sites_found", 0)
        
        if new_sites > 0:
            # Previous run was successful, continue with similar strategy
            queries = [
                "live sports stream free online",
                "watch sports streaming free", 
                "sports stream websites free",
                "streaming sports live free",
                "free sports streaming sites"
            ]
            tactical_plan = "Continue successful discovery pattern from previous run with slight variations to expand coverage"
            adaptations = f"Maintaining effective approach that discovered {new_sites} new sites"
        else:
            # Previous run struggled, try different approach  
            queries = [
                "sports streaming reddit communities",
                "live sports broadcasting free",
                "stream sports online free", 
                "sports stream aggregator sites",
                "free live sports streaming"
            ]
            tactical_plan = "Pivot to community-focused and aggregator-based discovery due to limited success in previous run"
            adaptations = f"Strategic pivot implemented due to {new_sites} sites found in previous mission"
        
        return {
            "mission_type": "adaptive_cognitive_fallback",
            "timestamp": datetime.now().isoformat(),
            "strategic_reasoning_process": {
                "status_review": f"Previous mission completed with {new_sites} new sites discovered. Analyzing performance for strategic evolution.",
                "strategic_goal": "Improve discovery rate through tactical adaptation based on previous mission analysis",
                "tactical_execution_plan": tactical_plan
            },
            "seed_queries": queries,
            "confidence_assessment": f"Moderate confidence in adapted approach based on {new_sites} previous results",
            "adaptations_made": adaptations,
            "expected_improvements": ["increased_discovery_rate", "improved_targeting", "better_community_coverage"]
        }