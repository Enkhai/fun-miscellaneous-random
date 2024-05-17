import json
import os
import time
from typing import Optional, List, Union

import requests
from loguru import logger
from requests.exceptions import HTTPError

REALTIME_URL = "https://realtime.oxylabs.io/v1"
ECT_URL = "https://ect.oxylabs.io/v1"


def request_scrape(url: str,
                   num_retries: Optional[int] = 5,
                   **kwargs) -> str:
    params = {
        'url': url,
        'geo_location': 'United States',
        'source': 'universal',
        **kwargs
    }

    logger.info(f"Requesting scrape with params: {params}")

    for i in range(num_retries):
        logger.info(f"Retry {i + 1} of {num_retries}...")
        resp = requests.get(REALTIME_URL + '/queries',
                            auth=(os.getenv('OXYLABS_USER'), os.getenv('OXYLABS_PASS')),
                            json=params)

        if resp.ok:
            logger.info(f"Scraping successful for URL `{url}`.")
            return resp.json()['results'][0]['content']

        logger.error(f"Failed scraping due to reason: `{resp.reason}`. Retrying...")
        time.sleep(4)

    logger.error(f"Failed to scrape URL `{url}`.")
    raise HTTPError(f"Failed to scrape URL `{url}`.")


def request_crawl(url: str,
                  crawl: List[str],
                  process: List[str],
                  max_depth: Optional[int] = 1,
                  source: Optional[str] = 'universal',
                  geo_location: Optional[str] = 'United States',
                  user_agent_type: Optional[str] = 'desktop',
                  render: Optional[str] = 'html',
                  output_type: Optional[str] = 'sitemap') -> Union[dict, list]:
    logger.info(f"Requesting crawl with params: {locals()}")

    api_url = ECT_URL + '/jobs'
    credentials = (os.getenv('OXYLABS_USER'), os.getenv('OXYLABS_PASS'))

    # make job
    job_resp = requests.post(api_url,
                             auth=credentials,
                             json={
                                 "url": url,
                                 "filters": {
                                     "crawl": crawl,
                                     "process": process,
                                     "max_depth": max_depth,
                                 },
                                 "scrape_params": {
                                     "source": source,
                                     "geo_location": geo_location,
                                     "user_agent_type": user_agent_type,
                                     "render": render
                                 },
                                 "output": {
                                     "type_": output_type
                                 }
                             }
                             )
    job_id = job_resp.json()['id']

    logger.info(f"Job submitted successfully with id: {job_id}")

    # wait for job
    while True:
        wait_resp = requests.get(f"{api_url}/{job_id}", auth=credentials)
        events = wait_resp.json()['events']
        if events and events[-1]['event'] == 'job_results_aggregated':
            logger.info("Job finished.")
            break
        time.sleep(1)

    # get job result chunks
    chunks_resp = requests.get(f"{api_url}/{job_id}/aggregate", auth=credentials)
    result_urls = [chunk['href'] for chunk in chunks_resp.json()['chunk_urls']]

    # get job results
    results = [] if output_type == 'sitemap' else {}
    for url in result_urls:
        result_resp = requests.get(url, auth=credentials)
        chunk_results = [json.loads(chunk) for chunk in result_resp.json()['chunks'] if chunk]
        if output_type == 'sitemap':
            results.extend(cr['url'] for cr in chunk_results)
        else:
            results.update({cr['url']: cr['content'] for cr in chunk_results})

    logger.info(f'Job results for job id `{job_id}` successfully retrieved.')

    return results
