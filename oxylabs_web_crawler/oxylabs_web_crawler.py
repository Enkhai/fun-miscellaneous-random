from typing import Optional

from fastapi import APIRouter, HTTPException
from loguru import logger

from schemas import CrawlURLRequest
from utils import request_scrape, request_crawl

router = APIRouter(prefix='/webscraping')


@router.get('/scrape')
async def scrape(url: str, num_retries: Optional[int] = 5):
    try:
        result = request_scrape(url, num_retries)
        return {'message': f"Scraping for URL `{url}` was successful.",
                'data': result}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=f"Error scraping URL `{url}`.")


@router.post('/crawl')
async def crawl(request: CrawlURLRequest):
    try:
        result = request_crawl(**request.model_dump())
        return {'message': f"Crawling for URL `{request.url}` has started.",
                'data': result}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=f"Error crawling URL `{request.url}`.")
