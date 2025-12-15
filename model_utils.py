import os
import google.generativeai as genai
from openai import AsyncOpenAI
from typing import List, Dict, Any
import asyncio

async def get_available_models(provider_config: Dict[str, Any]) -> List[str]:
    """
    Fetches available models for the given provider configuration.
    Returns a list of model names/IDs.
    """
    p_type = provider_config.get("type")
    api_key = provider_config.get("api_key")

    if not api_key and p_type != "custom":
        return []

    try:
        if p_type == "gemini":
            genai.configure(api_key=api_key)
            # Gemini list_models is synchronous in the SDK currently, but we can wrap it if needed.
            # We just run it directly.
            models = genai.list_models()
            return [m.name for m in models if 'gemini' in m.name]

        elif p_type == "openai":
            client = AsyncOpenAI(api_key=api_key)
            models = await client.models.list()
            return [m.id for m in models if m.id.startswith(('gpt-3.5', 'gpt-4'))]

        elif p_type == "custom":
            base_url = provider_config.get("base_url")
            effective_key = api_key if api_key else "sk-dummy"

            client = AsyncOpenAI(
                base_url=base_url,
                api_key=effective_key
            )
            models = await client.models.list()
            return [m.id for m in models]

    except Exception as e:
        # print(f"Error fetching models for {p_type}: {e}")
        # Return empty list on error to avoid breaking UI
        return []

    return []

async def get_response(provider_config: Dict[str, Any], model_name: str, messages: List[Dict[str, str]]) -> str:
    """
    Generates a response from the specified provider and model.
    messages format: [{"role": "user", "content": "..."}]
    """
    p_type = provider_config.get("type")
    api_key = provider_config.get("api_key")

    if not api_key and p_type != "custom":
        return "Error: API Key missing."

    try:
        if p_type == "gemini":
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)

            # Convert OpenAI-style messages to Gemini history
            gemini_history = []
            # We skip the last message as it will be the prompt
            for msg in messages[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg["content"]]})

            chat = model.start_chat(history=gemini_history)
            last_msg = messages[-1]['content']

            response = await chat.send_message_async(last_msg)
            return response.text

        elif p_type in ["openai", "custom"]:
            base_url = provider_config.get("base_url")
            effective_key = api_key if api_key else "sk-dummy"

            client = AsyncOpenAI(
                api_key=effective_key,
                base_url=base_url
            )

            response = await client.chat.completions.create(
                model=model_name,
                messages=messages
            )
            return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"
