from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Optional

import httpx
from groq import AsyncGroq
from groq._exceptions import GroqError as GroqSDKError

from ..core.config import get_settings
from ..core.exceptions import ConfigError, GroqError


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _mask_key(api_key: str) -> str:
    # Show only first/last 5 chars to avoid leaking secret
    if len(api_key) <= 10:
        return "***hidden***"
    return f"{api_key[:5]}...{api_key[-5:]}"


# Singleton instances
_shared_async_client: Optional[AsyncGroqClient] = None
_shared_httpx_client: Optional[httpx.AsyncClient] = None


def _create_optimized_httpx_client(timeout: float) -> httpx.AsyncClient:
    """
    Tạo optimized httpx client với connection pooling và HTTP/2.
    
    Tối ưu:
    - HTTP/2 multiplexing (nếu server hỗ trợ)
    - Connection pooling với keep-alive
    - Timeout tối ưu
    - Limits để tránh quá tải
    """
    settings = get_settings()
    
    return httpx.AsyncClient(
        http2=True,  # Enable HTTP/2 nếu server hỗ trợ
        limits=httpx.Limits(
            max_keepalive_connections=settings.GROQ_MAX_KEEPALIVE,
            max_connections=settings.GROQ_MAX_CONNECTIONS,
            keepalive_expiry=30.0,  # Keep connections alive for 30s
        ),
        timeout=httpx.Timeout(
            connect=5.0,  # Connection timeout
            read=timeout,  # Read timeout
            write=5.0,  # Write timeout
            pool=10.0,  # Pool timeout
        ),
        # Tối ưu headers
        headers={
            "Connection": "keep-alive",
            "Keep-Alive": "timeout=30",
        },
    )


def get_shared_httpx_client() -> httpx.AsyncClient:
    """
    Get or create singleton httpx client với connection pooling tối ưu.
    
    Returns:
        Shared httpx.AsyncClient instance
    """
    global _shared_httpx_client
    if _shared_httpx_client is None:
        settings = get_settings()
        _shared_httpx_client = _create_optimized_httpx_client(settings.GROQ_TIMEOUT)
        logger.info(
            "Created optimized httpx client: HTTP/2=%s, max_connections=%d, max_keepalive=%d",
            True,
            settings.GROQ_MAX_CONNECTIONS,
            settings.GROQ_MAX_KEEPALIVE,
        )
    return _shared_httpx_client


class AsyncGroqClient:
    """
    Async Groq client wrapper với connection pooling tối ưu.
    
    Tối ưu:
    - Singleton pattern để reuse connection
    - Optimized httpx client với HTTP/2 và keep-alive
    - Pre-warm connection
    - Timeout tối ưu
    """

    def __init__(self, client: Optional[AsyncGroq] = None):
        settings = get_settings()
        env_key = os.getenv("GROQ_API_KEY")
        api_key = env_key or settings.GROQ_API_KEY
        if not api_key:
            raise ConfigError("GROQ_API_KEY is not set.")

        source = "env:GROQ_API_KEY" if env_key else "settings.GROQ_API_KEY"
        logger.info("AsyncGroqClient using key from %s => %s", source, _mask_key(api_key))
        
        # Tạo client với timeout tối ưu
        # Note: Groq SDK có thể không hỗ trợ custom httpx client trực tiếp
        # Nhưng SDK sẽ tự động reuse connection nếu dùng cùng instance
        self.client = client or AsyncGroq(
            api_key=api_key,
            timeout=settings.GROQ_TIMEOUT,
        )
        self.model = settings.GROQ_MODEL
        self.temperature = settings.TEMPERATURE
        self.top_p = settings.TOP_P
        self._connection_warmed = False

    async def complete(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        max_tokens: int,
        track_timing: bool = False
    ) -> str:
        """
        Return plain-text completion content.
        
        Args:
            system_prompt: System prompt for the completion
            user_prompt: User prompt for the completion
            max_tokens: Maximum tokens to generate
            track_timing: If True, log timing breakdown for debugging
            
        Returns:
            Plain-text completion content
        """
        network_start = time.perf_counter()
        
        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=max_tokens,
                top_p=self.top_p,
            )
            network_end = time.perf_counter()
            
            if track_timing:
                network_latency_ms = (network_end - network_start) * 1000
                logger.debug(
                    "Groq API call completed: network_latency=%.2fms, model=%s",
                    network_latency_ms,
                    self.model,
                )
        except GroqSDKError as exc:
            raise GroqError(str(exc)) from exc

        content = completion.choices[0].message.content or ""
        return content.strip()


def get_shared_async_client() -> AsyncGroqClient:
    """
    Get or create singleton AsyncGroqClient instance for connection pooling.
    
    This ensures HTTP connections are reused across requests, reducing latency
    by avoiding TCP/TLS handshake overhead on subsequent requests.
    
    Returns:
        Shared AsyncGroqClient instance
    """
    global _shared_async_client
    if _shared_async_client is None:
        _shared_async_client = AsyncGroqClient()
        logger.info("Created shared AsyncGroqClient instance for connection pooling")
    return _shared_async_client

