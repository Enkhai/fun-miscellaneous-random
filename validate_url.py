from urllib.parse import urlparse, parse_qs

from loguru import logger


def validate_url(url: str) -> str:
    logger.info(f'Validating URL: {url}')

    if not (url.startswith('http://') or url.startswith('https://')):
        url = 'https://' + url

    try:
        parsed_url = urlparse(url)
        if all([parsed_url.scheme, parsed_url.netloc]):
            parse_qs(parsed_url.query)
            return url
    except Exception:
        logger.error(f'Invalid URL: {url}')
        raise ValueError(f'Invalid URL: {url}')
