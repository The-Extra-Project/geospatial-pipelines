import functools
import torch.distributed as dist
from contextlib import contextmanager
import torch

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



def get_world_size():
    r"""Get world size. How many GPUs are available in this job."""
    world_size = 1
    if dist.is_available():
        if dist.is_initialized():
            world_size = dist.get_world_size()
    return world_size


def dist_all_gather_tensor(tensor):
    r""" gather to all ranks """
    world_size = get_world_size()
    if world_size < 2:
        return [tensor]
    tensor_list = [
        torch.ones_like(tensor) for _ in range(dist.get_world_size())]
    with torch.no_grad():
        dist.all_gather(tensor_list, tensor)
    return tensor_list




def dist_all_reduce_tensor(tensor, reduce='mean'):
    r""" Reduce to all ranks """
    world_size = get_world_size()
    if world_size < 2:
        return tensor
    with torch.no_grad():
        dist.all_reduce(tensor)
        if reduce == 'mean':
            tensor /= world_size
        elif reduce == 'sum':
            pass
        else:
            raise NotImplementedError
    return tensor



def collate_test_data_batches(data_batches):
    """Aggregate the list of test data from all gpu's and process the results.
    Args:
        data_batches (list): List of (hierarchical) dictionaries, where leaf entries are tensors.
    Returns:
        data_gather (dict): (hierarchical) dictionaries, where leaf entries are concatenated tensors.
    """
    data_gather = dict()
    for key in data_batches[0].keys():
        data_list = [data[key] for data in data_batches]
        if isinstance(data_batches[0][key], dict):
            data_gather[key] = collate_test_data_batches(data_list)
        elif isinstance(data_batches[0][key], torch.Tensor):
            data_gather[key] = torch.cat(data_list, dim=0)
            data_gather[key] = torch.cat(dist_all_gather_tensor(data_gather[key].contiguous()), dim=0)
        else:
            raise TypeError
    return data_gather


def get_unique_test_data(data_gather, idx):
    """Aggregate the list of test data from all devices and process the results.
    Args:
        data_gather (dict): (hierarchical) dictionaries, where leaf entries are tensors.
        idx (tensor): sample indices.
    Returns:
        data_all (dict): (hierarchical) dictionaries, where leaf entries are tensors ordered by idx.
    """
    data_all = dict()
    for key, value in data_gather.items():
        if isinstance(value, dict):
            data_all[key] = get_unique_test_data(value, idx)
        elif isinstance(value, torch.Tensor):
            data_all[key] = []
            for i in range(max(idx) + 1):
                # If multiple occurrences of the same idx, just choose the first one. If no occurrence, just ignore.
                matches = (idx == i).nonzero(as_tuple=True)[0]
                if matches.numel() != 0:
                    data_all[key].append(value[matches[0]])
            data_all[key] = torch.stack(data_all[key], dim=0)
        else:
            raise TypeError
    return data_all


def trim_test_samples(data, max_samples=None):
    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = trim_test_samples(value, max_samples=max_samples)
        elif isinstance(value, torch.Tensor):
            if max_samples is not None:
                data[key] = value[:max_samples]
        else:
            raise TypeError



def broadcast_object_list(message, src=0):
    r"""broadcast the messages from across the GPU nodes"""
    if dist.is_available():
        if dist.is_initialized():
            torch.distributed.broadcast_object_list(message, src=src)
    return message

    