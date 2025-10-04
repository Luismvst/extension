# src/core/utils/http_client.py

import asyncio
import httpx
import logging

logger = logging.getLogger(__name__)

async def put_with_retry(url: str, headers: dict, payload: dict, max_retries: int = 3) -> httpx.Response:
    """Realiza un PUT con reintento automático al recibir 429 Too Many Requests."""
    attempt = 0
    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            response = await client.put(url, headers=headers, json=payload)
            if response.status_code != 429:
                response.raise_for_status()
                return response

            attempt += 1
            retry_after = response.headers.get("Retry-After")
            try:
                wait_time = int(retry_after) if retry_after else 2 ** attempt
            except ValueError:
                wait_time = 2 ** attempt

            if attempt > max_retries:
                logger.error(f"Exceeded max retries ({max_retries}) after repeated 429 responses.")
                response.raise_for_status()

            logger.warning(f"429 Too Many Requests — retrying in {wait_time}s (attempt {attempt}/{max_retries})")
            await asyncio.sleep(wait_time)
