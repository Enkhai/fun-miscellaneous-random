import threading
from typing import Any


def _wrapper(func, store, **kwargs):
    store['result'] = func(**kwargs)


def run_with_timeout(func, timeout, default_value, **kwargs) -> Any:
    '''Run a function with a timeout

    Args:
        func(callable): The function to run
        timeout(int): The timeout in seconds
        default_value(Any): The default value to return if the function times out
        **kwargs: The arguments to pass to the function

    Returns:
        Any: The result of the function if successful, else the default value
    '''

    store = {}
    thread = threading.Thread(target=_wrapper, args=(func, store), kwargs=kwargs)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        return default_value
    else:
        return store['result']
