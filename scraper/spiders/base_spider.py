# Base Spider for Real-Time Web Scraping
# Enforces P1: Unit tests for all new code

import scrapy
from scrapy.http import Response

class BaseSpider(scrapy.Spider):
    name = "base"
    
    def parse(self, response: Response):
        # Implement real-time parsing logic here
        # Placeholder: Extract title as example
        yield {
            "title": response.css("title::text").get(),
            "url": response.url,
            "timestamp": scrapy.utils.misc.now()
        }
