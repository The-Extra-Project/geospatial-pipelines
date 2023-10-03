import functools
import torch.distributed as dist
from contextlib import contextmanager

def master_only(func):
    r"""Apply this function only to the master GPU."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        r"""Simple function wrapper for the master function"""
        if get_rank() == 0:
            return func(*args, **kwargs)
        else:
            return None
    return wrapper


def is_master():
    r"""check if current process is the master"""
    return get_rank() == 0


def get_rank():
    r"""Get rank of the thread."""
    rank = 0
    if dist.is_available():
        if dist.is_initialized():
            rank = dist.get_rank()
    return rank

@master_only
def master_print(*args):
    r"""Print function that only runs on master GPU."""
    print(*args)
    