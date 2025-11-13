from __future__ import annotations

import concurrent.futures
from typing import Callable, Any

_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)


def run_in_thread(func: Callable, *args, **kwargs) -> concurrent.futures.Future:
    return _executor.submit(func, *args, **kwargs)
