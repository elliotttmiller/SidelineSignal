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
        V6.0 COGNITIVE ANALYSIS ENGINE
        
        Performs Chain-of-Thought with Self-Critique analysis using the Hugging Face LLM.
        This is the core of the V6.0 cognitive verification stage with full reasoning audit.

        Args:
            content: Raw text content from the website
            url: URL of the website (optional, for context)

        Returns:
            Dictionary containing structured V6.0 LLM analysis results with full reasoning process
        """
        if not self.api_key:
            logger.error("Hugging Face API key not available")
            return {
                "service_name": "Unknown",
                "is_sports_streaming_site": False,
                "full_reasoning_process": {
                    "initial_analysis": "Analysis unavailable - Hugging Face API key not configured",
                    "hypothesis": "Cannot form hypothesis without API access",
                    "self_critique": "Unable to perform self-critique without LLM access",
                    "conclusion": "Default negative conclusion due to API unavailability"
                },
                "final_confidence_score": 0,
                "error": "API key not configured"
            }

        try:
            # Prepare the V6.0 cognitive prompt
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
            logger.info(f"V6.0 Cognitive Analysis: Sending structured reasoning request to Hugging Face for: {url}")

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

            logger.info(f"V6.0 Cognitive Engine raw response: {llm_response}")

            # Parse V6.0 structured reasoning JSON response
            analysis_result = self._parse_llm_response(llm_response)

            logger.info(f"V6.0 Cognitive Analysis complete for {url}: "
                        f"Streaming={analysis_result.get('is_sports_streaming_site')} "
                        f"Confidence={analysis_result.get('final_confidence_score')}")

            return analysis_result

        except requests.exceptions.RequestException as e:
            logger.error(f"Hugging Face API request failed for {url}: {e}")
            return {
                "service_name": "Unknown",
                "is_sports_streaming_site": False,
                "full_reasoning_process": {
                    "initial_analysis": f"Analysis failed due to API request error: {str(e)}",
                    "hypothesis": "Cannot form hypothesis due to API communication failure",
                    "self_critique": "Self-critique unavailable - API request failed",
                    "conclusion": "Default negative conclusion due to API request failure"
                },
                "final_confidence_score": 0,
                "error": f"API request error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"V6.0 Cognitive Analysis failed for {url}: {e}")
            return {
                "service_name": "Unknown", 
                "is_sports_streaming_site": False,
                "full_reasoning_process": {
                    "initial_analysis": f"Critical analysis failure: {str(e)}",
                    "hypothesis": "Cannot form hypothesis due to system error",
                    "self_critique": "Self-critique unavailable due to system failure", 
                    "conclusion": "Default negative conclusion due to critical error"
                },
                "final_confidence_score": 0,
                "error": str(e)
            }

    def _craft_cognitive_prompt(self, content: str, url: str) -> str:
        """
        V6.0 STATE-OF-THE-ART COGNITIVE FRAMEWORK
        
        This implements the revolutionary Chain-of-Thought with Self-Critique methodology,
        creating a transparent, auditable, and hyper-reliable cognitive analysis engine.
        """
        # Truncate content to prevent token overflow
        max_content_length = 2000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."

        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a world-class web intelligence analyst. Your **sole and exclusive mission** is to determine if a website's primary purpose is to provide **free access to live or on-demand streams of sporting events**.

You must follow this **Cognitive Framework** precisely:
1. **<Initial_Analysis>**: Read the provided text. Identify keywords, themes, and any explicit mentions of sports, leagues, streaming, or schedules.
2. **<Formulate_Hypothesis>**: Based on your initial analysis, form a preliminary hypothesis about the site's purpose.
3. **<Self_Critique>**: Critically evaluate your own hypothesis. Are there alternative interpretations of the text? Could the keywords be misleading? Is there any evidence that contradicts your initial assessment? This is the most important step.
4. **<Final_Conclusion>**: Based on your hypothesis and your self-critique, make a final, definitive judgment.

You must respond ONLY with a single, valid JSON object. Do not include any other text. The JSON object must have the following structure:

<|eot_id|><|start_header_id|>user<|end_header_id|>

{{
  "service_name": "The user-friendly name of the service.",
  "is_sports_streaming_site": "A boolean (true or false).",
  "full_reasoning_process": {{
    "initial_analysis": "Your detailed notes from step 1.",
    "hypothesis": "Your hypothesis from step 2.",
    "self_critique": "Your critical evaluation from step 3.",
    "conclusion": "Your final conclusion from step 4."
  }},
  "final_confidence_score": "An integer between 0 and 100 representing your confidence in your final conclusion."
}}

Analyze this text:

URL: {url}

Content:
{content}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

        return prompt

    def _parse_llm_response(self, llm_response: str) -> Dict[str, Any]:
        """
        V6.0 COGNITIVE RESPONSE PARSER
        
        Parses the new structured reasoning format with full cognitive audit trail.
        Implements comprehensive error handling for the Chain-of-Thought JSON structure.
        """
        try:
            # Try direct JSON parsing first
            result = json.loads(llm_response)

            # Validate V6.0 required fields
            required_fields = [
                "service_name", "is_sports_streaming_site",
                "full_reasoning_process", "final_confidence_score"
            ]
            
            # Validate main fields
            for field in required_fields:
                if field not in result:
                    logger.warning(f"V6.0 LLM response missing required field: {field}")
                    if field == "is_sports_streaming_site":
                        result[field] = False
                    elif field == "full_reasoning_process":
                        result[field] = {
                            "initial_analysis": "Parse error - field missing",
                            "hypothesis": "Parse error - field missing", 
                            "self_critique": "Parse error - field missing",
                            "conclusion": "Parse error - field missing"
                        }
                    elif field == "final_confidence_score":
                        result[field] = 0
                    else:
                        result[field] = "Unknown"

            # Validate reasoning process structure
            if "full_reasoning_process" in result and isinstance(result["full_reasoning_process"], dict):
                reasoning_fields = ["initial_analysis", "hypothesis", "self_critique", "conclusion"]
                for field in reasoning_fields:
                    if field not in result["full_reasoning_process"]:
                        result["full_reasoning_process"][field] = "Missing reasoning step"

            return result

        except json.JSONDecodeError:
            logger.warning("Failed to parse V6.0 LLM JSON response, attempting fallback parsing")

            # Fallback: Extract JSON from response if it contains other text
            try:
                # Look for JSON object in the response
                start_idx = llm_response.find('{')
                end_idx = llm_response.rfind('}')

                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = llm_response[start_idx:end_idx + 1]
                    result = json.loads(json_str)

                    # Validate and fill missing V6.0 fields
                    if "service_name" not in result:
                        result["service_name"] = "Unknown"
                    if "is_sports_streaming_site" not in result:
                        result["is_sports_streaming_site"] = False
                    if "full_reasoning_process" not in result:
                        result["full_reasoning_process"] = {
                            "initial_analysis": "Fallback parsing - limited analysis available",
                            "hypothesis": "Unable to extract hypothesis from malformed response", 
                            "self_critique": "Self-critique unavailable due to parsing issues",
                            "conclusion": "Conclusion reached through fallback parsing"
                        }
                    if "final_confidence_score" not in result:
                        result["final_confidence_score"] = 50

                    logger.info("Successfully parsed V6.0 JSON from LLM response using fallback method")
                    return result

            except Exception as fallback_error:
                logger.error(f"V6.0 fallback JSON parsing also failed: {fallback_error}")

            # Final fallback: Return V6.0 compliant default structure
            logger.error(f"Could not parse V6.0 LLM response as JSON: {llm_response}")
            return {
                "service_name": "Unknown",
                "is_sports_streaming_site": False,
                "full_reasoning_process": {
                    "initial_analysis": "Failed to parse LLM response - no analysis available",
                    "hypothesis": "Unable to form hypothesis due to parsing failure",
                    "self_critique": "Cannot perform self-critique on unparseable response",  
                    "conclusion": "Default conclusion due to complete parsing failure"
                },
                "final_confidence_score": 0,
                "parse_error": "Complete JSON parsing failure"
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
