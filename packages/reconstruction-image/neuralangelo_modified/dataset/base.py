"""
class for functions in order to load the dataset into model.
"""



import torch
import tqdm
import threading
import queue
import importlib


from utils.gpu_jobs import master_print
from torch.utils.data import Dataset


class Dataset(Dataset):
    def __init__(self, is_inference=False, is_test=False):
        super().__init__()
        self.split = "test" if is_test else "val" if is_inference else "train"

    def _preload_worker(self, data_list, load_func, q, lock, idx_tqdm):
        # Keep preloading data in parallel.
        while True:
            idx = q.get()
            data_list[idx] = load_func(idx)
            with lock:
                idx_tqdm.update()
            q.task_done()

    def preload_threading(self, load_func, num_workers, data_str="images"):
        # Use threading to preload data in parallel.
        data_list = [None] * len(self)
        q = queue.Queue(maxsize=len(self))
        idx_tqdm = tqdm.tqdm(range(len(self)), desc=f"preloading {data_str} ({self.split})", leave=False)
        for i in range(len(self)):
            q.put(i)
        lock = threading.Lock()
        for ti in range(num_workers):
            t = threading.Thread(target=self._preload_worker,
                                 args=(data_list, load_func, q, lock, idx_tqdm), daemon=True)
            t.start()
        q.join()
        idx_tqdm.close()
        assert all(map(lambda x: x is not None, data_list))
        return data_list

    def __getitem__(self, idx):
        raise NotImplementedError

    def __len__(self):
        return len(self.list)


class continuousSampling(object):
    """ Sampler that repeats forever.
    Args:
        sampler (Sampler)
    """
    def __init__(self, sampler):
        self.sampler = sampler

    def __iter__(self):
        while True:
            yield from iter(self.sampler)

class MultiEpochsDatasetLoader(torch.utils.data.Dataloader):
    """
    class for loading the data in batches before running the epochs.
    taken reference implementation from:
    https://github.com/rwightman/pytorch-image-models/blob/master/timm/data/loader.py
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ## setting up the dataloader and sampler class
        super._Dataloader__initialized = False
        super.batch_sampler = continuousSampling(super.batch_sampler)
        super._Dataloader__initialized = True
        super.iterator = super.__iter__()
    
    def __len__(self):
        return len(self.batch_sampler.sampler)

    def __iter__(self):
        for i in range(len(self)):
            yield next(self.iterator)
        







