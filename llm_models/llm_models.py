"""
LLM Models configuration - ALL models defined here.

This file contains:
- Text generation LLM (GPT-4o-mini)
- Vision LLM for OCR (GPT-4o)
- Embeddings model (text-embedding-3-large)
- Async vision API caller for parallel processing
"""

import base64
import asyncio
import aiohttp
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from config.config import Config


# ============== TEXT GENERATION LLM ==============

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=Config.OPENAI_API_KEY,
)


def get_llm(temperature: float = 0.3, model: str = "gpt-4o-mini") -> ChatOpenAI:
    """Get LLM instance with custom settings."""
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=Config.OPENAI_API_KEY,
    )


# ============== EMBEDDINGS MODEL ==============

embeddings_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
    api_key=Config.OPENAI_API_KEY,
)


def get_embeddings() -> OpenAIEmbeddings:
    """Get embeddings model instance."""
    return embeddings_model


# ============== VISION LLM (for OCR) ==============

VISION_MODEL = "gpt-4.1-mini"
VISION_MAX_TOKENS = 4096
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


def call_vision_api(
    base64_image: str, 
    prompt: str, 
    system_prompt: str,
    detail: str = "high"
) -> str:
    """
    Synchronous call to OpenAI Vision API.
    
    Args:
        base64_image: Base64 encoded image
        prompt: User prompt
        system_prompt: System prompt
        detail: Image detail level (low/high)
    
    Returns:
        Extracted text from the image
    """
    import requests
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Config.OPENAI_API_KEY}"
    }
    
    payload = {
        "model": VISION_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": detail
                        }
                    }
                ]
            }
        ],
        "max_tokens": VISION_MAX_TOKENS
    }
    
    response = requests.post(
        OPENAI_API_URL,
        headers=headers,
        json=payload,
        timeout=160
    )
    
    if response.status_code != 200:
        raise Exception(f"Vision API error: {response.text}")
    
    return response.json()['choices'][0]['message']['content']


async def call_vision_api_async(
    session: aiohttp.ClientSession,
    base64_image: str, 
    prompt: str, 
    system_prompt: str,
    detail: str = "high"
) -> str:
    """
    Async call to OpenAI Vision API for parallel processing.
    
    Args:
        session: aiohttp session
        base64_image: Base64 encoded image
        prompt: User prompt
        system_prompt: System prompt
        detail: Image detail level
    
    Returns:
        Extracted text from the image
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Config.OPENAI_API_KEY}"
    }
    
    payload = {
        "model": VISION_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": detail
                        }
                    }
                ]
            }
        ],
        "max_tokens": VISION_MAX_TOKENS
    }
    
    async with session.post(
        OPENAI_API_URL,
        headers=headers,
        json=payload,
        timeout=aiohttp.ClientTimeout(total=120)
    ) as response:
        if response.status != 200:
            text = await response.text()
            raise Exception(f"Vision API error: {text}")
        
        result = await response.json()
        return result['choices'][0]['message']['content']


async def process_images_parallel(
    images_with_prompts: List[Dict],
    system_prompt: str,
    max_concurrent: int = 5
) -> List[str]:
    """
    Process multiple images in parallel.
    
    Args:
        images_with_prompts: List of {"image": base64, "prompt": str}
        system_prompt: System prompt for all
        max_concurrent: Max concurrent requests
    
    Returns:
        List of responses in order
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_one(session, item, index):
        async with semaphore:
            try:
                result = await call_vision_api_async(
                    session,
                    item["image"],
                    item["prompt"],
                    system_prompt
                )
                return (index, result, None)
            except Exception as e:
                return (index, None, str(e))
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            process_one(session, item, i) 
            for i, item in enumerate(images_with_prompts)
        ]
        results = await asyncio.gather(*tasks)
    
    # Sort by index and return
    results.sort(key=lambda x: x[0])
    return [(r[1], r[2]) for r in results]  # (response, error)
