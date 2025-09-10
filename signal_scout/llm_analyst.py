"""
LLM Analyst Module for SidelineSignal V5 - Hugging Face Cognitive Engine

This module implements the state-of-the-art Large Language Model analysis layer
that serves as the final cognitive verification stage in the V5 Triage Funnel.
Now powered by Hugging Face Inference API for professional deployment.
"""

import os
import json
import logging
import requests
from typing import Dict, Optional, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class LLMAnalyst:
    """
    State-of-the-art LLM Analyst for cognitive content verification via Hugging Face.
    
    This class implements the final verification stage of the V5 Hybrid Intelligence
    pipeline, using Hugging Face Inference API with structured prompts and JSON parsing.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the LLM Analyst with configuration.
        
        Args:
            config_path: Path to llm_config.json file
        """
        self.config = self._load_config(config_path)
        self.api_key = self._get_api_key()
        self.headers = self._setup_headers()
        
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
                "api_url": "https://api-inference.huggingface.co",
                "model_name": "meta-llama/Llama-3.1-8B-Instruct",
                "api_key_env": "HUGGINGFACE_API_KEY",
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
                "require_json_response": True,
                "use_few_shot_learning": True
            }
        }
    
    def _get_api_key(self) -> Optional[str]:
        """Get Hugging Face API key from environment variables."""
        api_key_env = self.config.get('llm_settings', {}).get('api_key_env', 'HUGGINGFACE_API_KEY')
        api_key = os.getenv(api_key_env)
        
        if not api_key:
            logger.warning(f"No Hugging Face API key found in environment variable: {api_key_env}")
            return None
        
        logger.info("Hugging Face API key loaded successfully")
        return api_key
    
    def _setup_headers(self) -> Dict[str, str]:
        """Setup HTTP headers for Hugging Face API requests."""
        if not self.api_key:
            return {}
        
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_cognitive_analysis(self, content: str, url: str = "") -> Dict[str, Any]:
        """
        Perform cognitive analysis of content using the Hugging Face LLM.
        
        This is the main entry point for the V5 cognitive verification stage.
        
        Args:
            content: Raw text content from the website
            url: URL of the website (optional, for context)
            
        Returns:
            Dictionary containing structured LLM analysis results
        """
        if not self.api_key:
            logger.error("Hugging Face API key not available")
            return {
                "service_name": "Unknown",
                "primary_category": "Unknown",
                "confidence_reasoning": "Hugging Face API key not available",
                "is_streaming_portal": False,
                "error": "API key not configured"
            }
        
        try:
            # Prepare the cognitive prompt
            prompt = self._craft_cognitive_prompt(content, url)
            
            # Get LLM settings
            llm_settings = self.config.get('llm_settings', {})
            api_url = llm_settings.get('api_url', 'https://api-inference.huggingface.co')
            model_name = llm_settings.get('model_name', 'meta-llama/Llama-3.1-8B-Instruct')
            
            # Prepare request payload for Hugging Face Inference API
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": llm_settings.get('max_tokens', 500),
                    "temperature": llm_settings.get('temperature', 0.1),
                    "return_full_text": False,
                    "do_sample": True
                }
            }
            
            # Make the Hugging Face API request
            logger.info(f"Sending cognitive analysis request to Hugging Face for: {url}")
            
            response = requests.post(
                f"{api_url}/models/{model_name}",
                headers=self.headers,
                json=payload,
                timeout=llm_settings.get('timeout', 30)
            )
            
            response.raise_for_status()
            
            # Extract the response
            response_data = response.json()
            
            # Handle different response formats from Hugging Face
            if isinstance(response_data, list) and len(response_data) > 0:
                llm_response = response_data[0].get("generated_text", "")
            elif isinstance(response_data, dict):
                llm_response = response_data.get("generated_text", "")
            else:
                llm_response = str(response_data)
            
            logger.info(f"Hugging Face raw response: {llm_response}")
            
            # Parse JSON response with robust error handling
            analysis_result = self._parse_llm_response(llm_response)
            
            logger.info(f"LLM cognitive analysis complete for {url}: "
                       f"Category={analysis_result.get('primary_category')} "
                       f"Streaming={analysis_result.get('is_streaming_portal')}")
            
            return analysis_result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Hugging Face API request failed for {url}: {e}")
            return {
                "service_name": "Unknown",
                "primary_category": "Error",
                "confidence_reasoning": f"Hugging Face API request failed: {str(e)}",
                "is_streaming_portal": False,
                "error": f"API request error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"LLM cognitive analysis failed for {url}: {e}")
            return {
                "service_name": "Unknown",
                "primary_category": "Error",
                "confidence_reasoning": f"LLM analysis failed: {str(e)}",
                "is_streaming_portal": False,
                "error": str(e)
            }
    
    def _craft_cognitive_prompt(self, content: str, url: str) -> str:
        """
        Engineer the state-of-the-art cognitive prompt for maximum reliability.
        
        This implements the meticulously engineered prompt with role-playing,
        few-shot learning, and structured output requirements optimized for Hugging Face models.
        """
        # Truncate content to prevent token overflow
        max_content_length = 2000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are an expert web content analyst. Your task is to analyze the provided text from a website and determine its purpose. You must respond ONLY with a single, valid JSON object. Do not include any other text or explanations.

<|eot_id|><|start_header_id|>user<|end_header_id|>

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
{content}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

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
        """Check if Hugging Face LLM service is available."""
        return self.api_key is not None and len(self.headers) > 0
    
    def get_v3_threshold(self) -> float:
        """Get the V3 confidence threshold for triggering LLM analysis."""
        return self.config.get('v4_integration', {}).get('v3_confidence_threshold', 0.7)


def create_llm_analyst(config_path: Optional[str] = None) -> LLMAnalyst:
    """Factory function to create an LLM Analyst instance."""
    return LLMAnalyst(config_path)