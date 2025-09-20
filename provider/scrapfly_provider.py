import aiohttp
import os
from typing import Dict, Optional
from abc import ABC, abstractmethod
from typing import override
from provider import ProviderSystem
import logging
import asyncio
import datetime

logger = logging.getLogger(__name__)

class ScrapflyProvider(ProviderSystem):
    
    def __init__(self):
        self.api_key = None
        self.session = None
        self.base_url = "https://api.scrapfly.io/scrape"

    async def initialize(self, api_key: Optional[str] = None, **kwargs) -> None:
        """Инициализация Scrapfly провайдера"""
        self.api_key = api_key or os.getenv("SCRAPFLY_KEY")
        if not self.api_key:
            raise ValueError("SCRAPFLY_KEY not found in environment variables")
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={'Accept': 'application/json'}
        )
        
        logger.info("Scrapfly provider initialized successfully")

    async def check(self, url: str) -> Dict:
        if not self.session:
            raise RuntimeError("Provider not initialized. Call initialize() first.")

        try:
            params = {
                'key': self.api_key,
                'url': url,
                'asp': 'true',
                'render_js': 'false',
                'country': 'us'
            }

            start_time = asyncio.get_event_loop().time()
            
            async with self.session.get(
                self.base_url,
                params=params,
                timeout=30
            ) as response:
                
                response_time_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
                
                if response.status != 200:
                    return self._create_error_result(
                        f"Scrapfly API error: HTTP {response.status}",
                        response_time_ms
                    )
                
                response_data = await response.json()
                
                success = response_data.get('success', False)
                if not success:
                    error_msg = response_data.get('message', 'Unknown Scrapfly error')
                    return self._create_error_result(
                        f"Scrapfly error: {error_msg}",
                        response_time_ms
                    )
                
                result = response_data.get('result', {})
                http_status = result.get('status_code', 0)
                content = result.get('content', '')
                
                ssl_info = result.get('ssl', {})
                ssl_valid = ssl_info.get('valid', True)
                ssl_days_left = self._calculate_ssl_days_left(ssl_info)
                
                return {
                    'status_code': http_status,
                    'error': None,
                    'response_time_ms': response_time_ms,
                    'ssl_valid': ssl_valid,
                    'ssl_days_left': ssl_days_left,
                    'content': content,
                    'success': True
                }

        except aiohttp.ClientError as e:
            logger.error(f"Network error during Scrapfly check: {str(e)}")
            return self._create_error_result(f"Network error: {str(e)}", 0)
            
        except asyncio.TimeoutError:
            logger.warning(f"Timeout during Scrapfly check for {url}")
            return self._create_error_result("Request timeout (30s)", 0)
            
        except Exception as e:
            logger.exception(f"Unexpected error during Scrapfly check: {str(e)}")
            return self._create_error_result(f"Unexpected error: {str(e)}", 0)

    def _calculate_ssl_days_left(self, ssl_info: Dict) -> Optional[int]:
        not_after = ssl_info.get('not_after')
        if not not_after:
            return None
            
        try:
            expiry_date = datetime.fromisoformat(not_after.replace('Z', '+00:00'))
            days_left = (expiry_date - datetime.utcnow()).days
            return max(0, days_left)
        except (ValueError, TypeError):
            return None

    def _create_error_result(self, error_message: str, response_time_ms: int) -> Dict:
        """Создает результат с ошибкой"""
        return {
            'status_code': 0,
            'error': error_message,
            'response_time_ms': response_time_ms,
            'ssl_valid': False,
            'ssl_days_left': None,
            'content': None,
            'success': False
        }

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Scrapfly provider session closed")