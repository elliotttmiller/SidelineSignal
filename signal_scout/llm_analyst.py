"""
LLM Analyst Module for SidelineSignal V4 - Hybrid Intelligence Engine

This module implements the state-of-the-art Large Language Model analysis layer
that serves as the final cognitive verification stage in the V4 Triage Funnel.
"""

import os
import json
import logging
from typing import Dict, Optional, Any
from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMAnalyst:
    """
    State-of-the-art LLM Analyst for cognitive content verification.
    
    This class implements the final verification stage of the V4 Hybrid Intelligence
    pipeline, using structured prompts and JSON parsing for reliable machine readability.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the LLM Analyst with configuration.
        
        Args:
            config_path: Path to llm_config.json file
        """
        self.config = self._load_config(config_path)
        self.client = None
        self._initialize_client()
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load LLM configuration from JSON file."""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'llm_config.json')
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"LLM configuration loaded from: {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load LLM configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if config file not found."""
        logger.warning("Using default LLM configuration")
        return {
            "llm_settings": {
                "api_url": "http://localhost:1234/v1",
                "model_name": "local-model",
                "api_key": "lm-studio",
                "max_tokens": 500,
                "temperature": 0.1,
                "timeout": 30
            },
            "v4_integration": {
                "v3_confidence_threshold": 0.7,
                "enable_llm_verification": True,
                "llm_verification_timeout": 30
            },
            "prompt_engineering": {
                "system_role": "expert web content analyst",
                "require_json_response": true,
                "use_few_shot_learning": true
            }
        }
    
    def _initialize_client(self):
        """Initialize the OpenAI client for LM Studio."""
        try:
            llm_settings = self.config.get('llm_settings', {})
            
            self.client = OpenAI(
                base_url=llm_settings.get('api_url', 'http://localhost:1234/v1'),
                api_key=llm_settings.get('api_key', 'lm-studio')
            )
            
            logger.info("LLM client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            self.client = None
    
    def get_cognitive_analysis(self, content: str, url: str = "") -> Dict[str, Any]:
        """
        Perform cognitive analysis of content using the LLM.
        
        This is the main entry point for the V4 cognitive verification stage.
        
        Args:
            content: Raw text content from the website
            url: URL of the website (optional, for context)
            
        Returns:
            Dictionary containing structured LLM analysis results
        """
        if not self.client:
            logger.error("LLM client not available")
            return {
                "service_name": "Unknown",
                "primary_category": "Unknown",
                "confidence_reasoning": "LLM client not available",
                "is_streaming_portal": False,
                "error": "LLM client initialization failed"
            }
        
        try:
            # Prepare the cognitive prompt
            prompt = self._craft_cognitive_prompt(content, url)
            
            # Get LLM settings
            llm_settings = self.config.get('llm_settings', {})
            
            # Make the LLM request
            logger.info(f"Sending cognitive analysis request to LLM for: {url}")
            
            response = self.client.chat.completions.create(
                model=llm_settings.get('model_name', 'local-model'),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert web content analyst. You must respond ONLY with valid JSON."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=llm_settings.get('max_tokens', 500),
                temperature=llm_settings.get('temperature', 0.1),
                timeout=llm_settings.get('timeout', 30)
            )
            
            # Extract and parse the response
            llm_response = response.choices[0].message.content.strip()
            logger.info(f"LLM raw response: {llm_response}")
            
            # Parse JSON response with robust error handling
            analysis_result = self._parse_llm_response(llm_response)
            
            logger.info(f"LLM cognitive analysis complete for {url}: "
                       f"Category={analysis_result.get('primary_category')} "
                       f"Streaming={analysis_result.get('is_streaming_portal')}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"LLM cognitive analysis failed for {url}: {e}")
            return {
                "service_name": "Unknown",
                "primary_category": "Error",
                "confidence_reasoning": f"LLM analysis failed: {str(e)}",
                "is_streaming_portal": false,
                "error": str(e)
            }
    
    def _craft_cognitive_prompt(self, content: str, url: str) -> str:
        """
        Engineer the state-of-the-art cognitive prompt for maximum reliability.
        
        This implements the meticulously engineered prompt with role-playing,
        few-shot learning, and structured output requirements.
        """
        # Truncate content to prevent token overflow
        max_content_length = 2000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        prompt = f"""You are an expert web content analyst. Your task is to analyze the provided text from a website and determine its purpose. You must respond ONLY with a single, valid JSON object. Do not include any other text or explanations.

Here is an example of the perfect response format:
{{
  "service_name": "StreamEast",
  "primary_category": "Sports Streaming",
  "confidence_reasoning": "The text explicitly mentions live NFL games, provides streaming links, and includes sports schedules.",
  "is_streaming_portal": true
}}

Categories to choose from:
- "Sports Streaming" (for sites that stream live sports)
- "General Streaming" (for sites that stream movies/TV shows)
- "Sports News" (for sports news and information sites)
- "General News" (for general news websites)
- "E-commerce" (for shopping and retail sites)
- "Social Media" (for social platforms and forums)
- "Other" (for sites that don't fit other categories)

Now, analyze the following text and provide your response in the exact JSON format shown above:

URL: {url}

Content:
{content}"""

        return prompt
    
    def _parse_llm_response(self, llm_response: str) -> Dict[str, Any]:
        """
        Parse LLM response with robust JSON handling.
        
        Implements comprehensive error handling and fallback parsing
        to ensure machine readability of LLM outputs.
        """
        try:
            # Try direct JSON parsing first
            result = json.loads(llm_response)
            
            # Validate required fields
            required_fields = ["service_name", "primary_category", "confidence_reasoning", "is_streaming_portal"]
            for field in required_fields:
                if field not in result:
                    logger.warning(f"LLM response missing required field: {field}")
                    result[field] = "Unknown" if field != "is_streaming_portal" else False
            
            return result
            
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse LLM JSON response, attempting fallback parsing")
            
            # Fallback: Extract JSON from response if it contains other text
            try:
                # Look for JSON object in the response
                start_idx = llm_response.find('{')
                end_idx = llm_response.rfind('}')
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = llm_response[start_idx:end_idx + 1]
                    result = json.loads(json_str)
                    
                    # Validate and fill missing fields
                    required_fields = ["service_name", "primary_category", "confidence_reasoning", "is_streaming_portal"]
                    for field in required_fields:
                        if field not in result:
                            result[field] = "Unknown" if field != "is_streaming_portal" else False
                    
                    logger.info("Successfully parsed JSON from LLM response using fallback method")
                    return result
                    
            except Exception as fallback_error:
                logger.error(f"Fallback JSON parsing also failed: {fallback_error}")
            
            # Final fallback: Return default structure
            logger.error(f"Could not parse LLM response as JSON: {llm_response}")
            return {
                "service_name": "Unknown",
                "primary_category": "Other",
                "confidence_reasoning": "Failed to parse LLM response",
                "is_streaming_portal": False,
                "parse_error": "JSON parsing failed"
            }
    
    def is_available(self) -> bool:
        """Check if LLM service is available."""
        return self.client is not None
    
    def get_v3_threshold(self) -> float:
        """Get the V3 confidence threshold for triggering LLM analysis."""
        return self.config.get('v4_integration', {}).get('v3_confidence_threshold', 0.7)


def create_llm_analyst(config_path: Optional[str] = None) -> LLMAnalyst:
    """Factory function to create an LLM Analyst instance."""
    return LLMAnalyst(config_path)