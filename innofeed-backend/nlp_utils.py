import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
import requests
from typing import List
import time

# Get the Hugging Face API Key from the environment variables
HF_API_KEY = os.getenv("HF_API_KEY")

# Working models confirmed on Hugging Face Inference API (November 2024)
# Philipp Schmid model for summarization - actively maintained
# MoritzLaurer model for zero-shot classification - top rated and active
API_URL_SUMMARIZATION = "https://api-inference.huggingface.co/models/Falconsai/text_summarization"
API_URL_CLASSIFICATION = "https://api-inference.huggingface.co/models/MoritzLaurer/deberta-v3-large-zeroshot-v2.0"

def summarize_text(text: str) -> str:
    """
    Generates an abstractive summary using Hugging Face's Inference API.
    Model: Falconsai/text_summarization (T5-based, actively maintained)
    Fallback: Returns truncated text if API unavailable
    """
    if not text or len(text.strip()) == 0:
        return "No content available"
    
    # If no API key, use fallback
    if not HF_API_KEY:
        return text.strip()[:200] + "..."

    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    # Truncate text (T5 models have token limits)
    max_length = 800
    truncated_text = text[:max_length] if len(text) > max_length else text
    
    payload = {
        "inputs": truncated_text,
        "parameters": {
            "max_length": 150,
            "min_length": 30,
            "do_sample": False
        },
        "options": {
            "wait_for_model": True,
            "use_cache": True
        }
    }

    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = requests.post(
                API_URL_SUMMARIZATION, 
                headers=headers, 
                json=payload, 
                timeout=45
            )
            
            # Handle various response codes
            if response.status_code == 503:
                try:
                    error_data = response.json()
                    if "estimated_time" in error_data and attempt < max_retries - 1:
                        wait_time = min(error_data["estimated_time"], 15)
                        print(f"Model loading, waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                except:
                    pass
                return text.strip()[:200] + "..."
            
            if response.status_code in [429, 410]:
                return text.strip()[:200] + "..."
            
            response.raise_for_status()
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and "summary_text" in result[0]:
                    return result[0]["summary_text"]
            elif isinstance(result, dict):
                if "summary_text" in result:
                    return result["summary_text"]
                elif "error" in result:
                    return text.strip()[:200] + "..."
                
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                return text.strip()[:200] + "..."
            time.sleep(2)
        except requests.exceptions.RequestException:
            if attempt == max_retries - 1:
                return text.strip()[:200] + "..."
            time.sleep(2)
        except Exception:
            return text.strip()[:200] + "..."
    
    return text.strip()[:200] + "..."


def categorize_text(text: str, categories: List[str]) -> str:
    """
    Categorizes text using zero-shot classification.
    Model: MoritzLaurer/deberta-v3-large-zeroshot-v2.0 (top-rated, actively maintained)
    Fallback: Returns first category if API unavailable
    """
    if not text or len(text.strip()) == 0:
        return categories[0] if categories else "Uncategorized"
    
    if not HF_API_KEY:
        return categories[0] if categories else "Uncategorized"

    if not categories:
        return "Uncategorized"

    headers = {"Authorization": f"Bearer {HF_API_KEY}"}

    # Truncate text (DeBERTa has 512 token limit)
    max_length = 1000
    truncated_text = text[:max_length] if len(text) > max_length else text

    payload = {
        "inputs": truncated_text,
        "parameters": {
            "candidate_labels": categories,
            "multi_label": False
        },
        "options": {
            "wait_for_model": True,
            "use_cache": True
        }
    }

    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = requests.post(
                API_URL_CLASSIFICATION, 
                headers=headers, 
                json=payload, 
                timeout=45
            )
            
            # Handle various response codes
            if response.status_code == 503:
                try:
                    error_data = response.json()
                    if "estimated_time" in error_data and attempt < max_retries - 1:
                        wait_time = min(error_data["estimated_time"], 15)
                        print(f"Model loading, waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                except:
                    pass
                return categories[0]
            
            if response.status_code in [429, 410]:
                return categories[0]
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the top label
            if isinstance(result, dict) and "labels" in result:
                if result["labels"] and len(result["labels"]) > 0:
                    return result["labels"][0]
                elif "error" in result:
                    return categories[0]
                    
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                return categories[0]
            time.sleep(2)
        except requests.exceptions.RequestException:
            if attempt == max_retries - 1:
                return categories[0]
            time.sleep(2)
        except Exception:
            return categories[0]
    
    return categories[0] if categories else "Uncategorized"