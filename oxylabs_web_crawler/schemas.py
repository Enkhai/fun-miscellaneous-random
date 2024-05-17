import re
from typing import Optional, Literal

import validators
from pydantic import BaseModel, field_validator


class CrawlURLRequest(BaseModel):
    url: str
    crawl: Optional[list[str]] = ['.*']
    process: Optional[list[str]] = ['.*']
    max_depth: Optional[int] = 1
    source: Optional[str] = 'universal'
    geo_location: Optional[str] = 'United States'
    user_agent_type: Optional[str] = 'desktop'
    render: Optional[Literal['html', 'png']] = 'html'
    output_type: Optional[Literal['sitemap', 'html', 'parsed']] = 'sitemap'

    @field_validator('max_depth')
    def validate_depth(cls, max_depth: int):
        if max_depth < -1:
            raise ValueError('Depth must be at least 1')
        return max_depth

    @field_validator('url')
    def validate_url(cls, url: str):
        if not validators.url(url):
            raise ValueError('Invalid URL')
        return url

    @field_validator('crawl')
    def validate_crawl(cls, crawl: list[str]):
        if not crawl:
            raise ValueError('Crawl list must not be empty')
        for c in crawl:
            try:
                re.compile(c)
            except re.error:
                raise ValueError(f'Invalid regex: {c}')
        return crawl

    @field_validator('process')
    def validate_process(cls, process: list[str]):
        if not process:
            raise ValueError('Process list must not be empty')
        for p in process:
            try:
                re.compile(p)
            except re.error:
                raise ValueError(f'Invalid regex: {p}')
        return process
