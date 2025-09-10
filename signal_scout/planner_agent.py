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
        """Generate the initial mission plan for the first run."""
        logger.info("PlannerAgent executing GENESIS RUN - creating foundational strategy")
        
        if not self.client or not self.is_available():
            logger.warning("LLM not available - using fallback genesis plan")
            return self._get_fallback_genesis_plan()
        
        genesis_prompt = f"""
{self.genesis_objective}

As an autonomous planning AI, create an intelligent discovery strategy. Generate search queries that will help discover active sports streaming websites.

Consider these aspects:
1. Popular sports (NFL, NBA, MLB, soccer, hockey)
2. Different search angles (live streaming, free sports, specific teams)
3. Community-driven terms (Reddit terms, streaming communities)
4. Technical terms (stream, live TV, sports broadcasts)

Respond with ONLY a valid JSON object in this exact format:
{{
    "mission_type": "genesis",
    "timestamp": "{datetime.now().isoformat()}",
    "strategy": "Brief description of the discovery strategy",
    "seed_queries": ["query1", "query2", "query3", "query4", "query5"],
    "reasoning": "Explanation of why these queries were chosen"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config["llm_settings"]["model_name"],
                messages=[
                    {"role": "system", "content": "You are an expert autonomous planning AI for web discovery missions."},
                    {"role": "user", "content": genesis_prompt}
                ],
                max_tokens=self.config["llm_settings"]["max_tokens"],
                temperature=self.config["llm_settings"]["temperature"],
                timeout=self.config["llm_settings"]["timeout"]
            )
            
            plan_text = response.choices[0].message.content.strip()
            logger.info(f"PlannerAgent received LLM response: {plan_text[:100]}...")
            
            # Parse JSON response
            plan = json.loads(plan_text)
            
            # Validate required fields
            if not all(key in plan for key in ["strategy", "seed_queries"]):
                raise ValueError("Missing required fields in plan")
            
            logger.info("PlannerAgent generated genesis plan successfully")
            return plan
            
        except Exception as e:
            logger.error(f"PlannerAgent genesis planning failed: {e}")
            return self._get_fallback_genesis_plan()
    
    def _generate_adaptive_plan(self, previous_report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an adaptive mission plan based on previous results."""
        logger.info("PlannerAgent executing ADAPTIVE RUN - analyzing previous results")
        
        if not self.client or not self.is_available():
            logger.warning("LLM not available - using fallback adaptive plan")
            return self._get_fallback_adaptive_plan(previous_report)
        
        adaptive_prompt = f"""
Analyze this mission report from the previous discovery run:

{json.dumps(previous_report, indent=2)}

Based on these results, create an improved discovery strategy. Consider:
1. Which queries/methods were most effective?
2. What types of sites were successfully found?
3. Where did the mission struggle or fail?
4. How can the strategy be evolved for better results?

Respond with ONLY a valid JSON object in this exact format:
{{
    "mission_type": "adaptive",
    "timestamp": "{datetime.now().isoformat()}",
    "strategy": "Updated strategy based on analysis",
    "seed_queries": ["evolved_query1", "evolved_query2", "evolved_query3", "evolved_query4", "evolved_query5"],
    "reasoning": "Why this strategy improves on previous results",
    "adaptations": "Specific changes made based on previous report"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config["llm_settings"]["model_name"],
                messages=[
                    {"role": "system", "content": "You are an expert autonomous planning AI that learns from previous mission results to improve strategy."},
                    {"role": "user", "content": adaptive_prompt}
                ],
                max_tokens=self.config["llm_settings"]["max_tokens"],
                temperature=self.config["llm_settings"]["temperature"],
                timeout=self.config["llm_settings"]["timeout"]
            )
            
            plan_text = response.choices[0].message.content.strip()
            logger.info(f"PlannerAgent received adaptive LLM response: {plan_text[:100]}...")
            
            # Parse JSON response
            plan = json.loads(plan_text)
            
            # Validate required fields
            if not all(key in plan for key in ["strategy", "seed_queries"]):
                raise ValueError("Missing required fields in adaptive plan")
            
            logger.info("PlannerAgent generated adaptive plan successfully")
            return plan
            
        except Exception as e:
            logger.error(f"PlannerAgent adaptive planning failed: {e}")
            return self._get_fallback_adaptive_plan(previous_report)
    
    def _get_fallback_genesis_plan(self) -> Dict[str, Any]:
        """Fallback genesis plan when LLM is unavailable."""
        return {
            "mission_type": "genesis_fallback",
            "timestamp": datetime.now().isoformat(),
            "strategy": "Genesis fallback strategy focusing on core sports streaming discovery",
            "seed_queries": [
                "watch NFL live free streaming",
                "soccer stream free online",
                "NBA live stream reddit",
                "MLB streaming sites free",
                "live sports streaming free"
            ],
            "reasoning": "Fallback genesis plan covering major sports with community-focused terms"
        }
    
    def _get_fallback_adaptive_plan(self, previous_report: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback adaptive plan when LLM is unavailable."""
        # Simple adaptive logic - if we found sites, double down on successful patterns
        new_sites = previous_report.get("new_sites_found", 0)
        
        if new_sites > 0:
            # Previous run was successful, continue with similar strategy
            queries = [
                "live sports stream free online",
                "watch sports streaming free",
                "sports stream websites free",
                "streaming sports live free",
                "free sports streaming sites"
            ]
            strategy = "Continue successful discovery pattern from previous run"
        else:
            # Previous run struggled, try different approach
            queries = [
                "sports streaming reddit communities",
                "live sports broadcasting free",
                "stream sports online free",
                "sports stream aggregator sites",
                "free live sports streaming"
            ]
            strategy = "Pivot strategy due to limited success in previous run"
        
        return {
            "mission_type": "adaptive_fallback",
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy,
            "seed_queries": queries,
            "reasoning": f"Fallback adaptive plan based on {new_sites} sites found in previous run",
            "adaptations": "Adjusted query focus based on previous results"
        }