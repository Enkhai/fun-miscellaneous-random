import time
from functools import wraps
from typing import Any

from loguru import logger


def exp_backoff(func: callable,
                backoff_seconds: int = 30,
                multiplier: float = 1.2,
                max_retries: int = 5,
                max_time: int = 60,
                wait_before: bool = False,
                ) -> callable:
    '''Exponential fallback decorator

    Args:
        func(callable): The function to decorate
        backoff_seconds(int): The initial number of seconds to wait before retrying
        multiplier(float): The multiplier to use for the backoff
        max_retries(int): The maximum number of retries
        max_time(int): The maximum time to wait before retrying
        wait_before(bool): Whether to wait before or after the retry

    Returns:
        callable: The decorated function
    '''

    @wraps(func)
    @logger.catch(message="Failed to execute function.")
    def wrapper(*args, **kwargs):
        wait_seconds = backoff_seconds
        for i in range(max_retries):
            logger.info(f"Retry {i + 1} of {max_retries}...")

            if wait_before:
                logger.info(f"Waiting {wait_seconds} seconds...")
                time.sleep(wait_seconds)

            response = func(*args, **kwargs)
            if response is not None:
                return response

            logger.info(f"Retry {i + 1} of {max_retries} failed.")

            if not wait_before:
                logger.info(f"Waiting {wait_seconds} seconds...")
                time.sleep(wait_seconds)

            wait_seconds *= multiplier
            wait_seconds = min(wait_seconds, max_time)

        logger.error(f"Failed after {max_retries} retries.")

    return wrapper


def run_with_backoff(func: callable, func_args: dict, **kwargs) -> Any:
    '''Run a function with exponential fallback

    Args:
        func(callable): The function to run
        func_args(dict): The arguments to pass to the function
        **kwargs: The arguments to pass to the fallback decorator. See `exp_fallback` for more details.

    Returns:
        Any: The result of the function
    '''
    fallback_func = exp_backoff(func, **kwargs)
    return fallback_func(**func_args)
