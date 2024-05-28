from concurrent.futures import ThreadPoolExecutor


def parallel_func(args):
    '''Run a function and if the result is not None, store it

    Args:
        args(tuple): A tuple of the function, the arguments, the key to store the result under and the store
    '''

    func, kwargs, store_key, store = args
    res = func(**kwargs)
    if res is not None:
        store[store_key] = res


def parallel_call(func: callable,
                  dynamic_args: list[dict],
                  static_args: dict,
                  max_threads: int = 16):
    '''Run a function in parallel

    Args:
        func(callable): The function to run
        dynamic_args(list[dict]): A list of arguments to pass to the function
        static_args(dict): The static arguments to pass to the function
        max_threads(int): The maximum number of threads to use. Defaults to 10.

    Returns:
        list: The list of results
    '''

    store = {i: None for i in range(len(dynamic_args))}
    iterables = [(func, {**static_args, **current_args}, store_key, store)
                 for store_key, current_args in enumerate(dynamic_args)]
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        for _ in executor.map(parallel_func, iterables):
            pass

    result = list(map(lambda x: x[1], sorted(store.items())))
    return result
