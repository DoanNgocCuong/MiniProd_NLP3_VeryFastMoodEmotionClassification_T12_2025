import time
from contextlib import contextmanager
from typing import Iterator, Tuple


@contextmanager
def track_time() -> Iterator[Tuple[float, float]]:
    """Context manager to measure elapsed time in ms."""
    start = time.perf_counter()
    yield (start, time.perf_counter())
    # consumer computes elapsed; we avoid side effects here


def elapsed_ms(start: float) -> float:
    """Return elapsed milliseconds since start perf counter."""
    return (time.perf_counter() - start) * 1000

