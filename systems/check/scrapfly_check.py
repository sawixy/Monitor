from typing import override
import os
from check import CheckSystem
from scrapfly import ScrapeConfig, ScrapflyClient, ScrapeApiResponse

class ScrapFly(CheckSystem):
    @override
    async def check(self, url) -> bool:
        api_key = os.getenv("SCRAPFLY_API_KEY")

        if not api_key:
            raise ValueError("SCRAPFLY_API_KEY not found in env")

        scrapfly = await ScrapflyClient(key=api_key)

        api_response: ScrapeApiResponse = await scrapfly.scrape(
            ScrapeConfig(
                url=url,
                render_js=False,
                asp=True
            )
        )

        if api_response.response.status_code < 400:
            return True
        else:
            return False