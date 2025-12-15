import json
import os
from typing import List, Dict, Any


CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "gemini_key": "",
    "openai_key": "",
    "custom_providers": []
}

def load_config() -> Dict[str, Any]:
    """Loads the configuration from config.json. Returns default if not found."""
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            # Ensure all keys exist (migration support)
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]):
    """Saves the configuration to config.json."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

def get_provider_config(provider_name: str, config: Dict[str, Any]) -> Dict[str, str]:
    """Helper to construct a config object for a specific provider."""
    if provider_name == "Gemini":
        return {
            "type": "gemini",
            "api_key": config.get("gemini_key", "")
        }
    elif provider_name == "OpenAI":
        return {
            "type": "openai",
            "api_key": config.get("openai_key", ""),
            "base_url": None # Uses default
        }
    else:
        # Search in custom providers
        for p in config.get("custom_providers", []):
            if p["name"] == provider_name:
                return {
                    "type": "custom",
                    "api_key": p["api_key"],
                    "base_url": p["base_url"]
                }
    return {}
