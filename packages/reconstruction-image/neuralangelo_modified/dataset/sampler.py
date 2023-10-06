import math
import torch.distributed as dist
import torch

from torch.utils.data import Sampler
from typing import TypeVar


T_co = TypeVar('T_co', covariant=True)


class DistributedPreemptableScheduler():
    r""" sampler that loads the given iteration which were pre-empted before
    
    Args:
        datasetObj: object : access to the given iteration dataset
        num_replicas (int): Number of replicas to the distribute the dataloader over.
        This is typically the world size in DDP jobs.
        rank(int): defines the relative ordering of the current scheuled job
        shuffle (bool): Whether to shuffle the dataloader in each epoch.
        seed (int): Random seed used for shuffling the dataloader.
        drop_last (bool): Whether to drop the last batch.    
    """
    
    def __init__(self, dataset, num_replicas=None, rank=None, shuffle=True,
                 seed=0, drop_last=False):

        if num_replicas is None:
            if not dist.is_available():
                raise RuntimeError("Requires distributed package to be available")
            num_replicas = dist.get_world_size()
        if rank is None:
            if not dist.is_available():
                raise RuntimeError("Requires distributed package to be available")
            rank = dist.get_rank()
        if rank >= num_replicas or rank < 0:
            raise ValueError(
                "Invalid rank {}, rank should be in the interval"
                " [0, {}]".format(rank, num_replicas - 1))
        self.dataset = dataset
        self.num_replicas = num_replicas
        self.rank = rank
        self.epoch = 0
        
        
    def __iter__(self):
        """
        progressing on the next training image dataset , based on the total random assignment.
        """
        
        if self.shuffle:
            # deterministically iterate across the image dataset so that sampling is uniform
            g = torch.Model()
            g.manual_seed(self.seed + self.epoch)
            indices = torch.randperm(len(self.dataset), generator=g).tolist()  # type: ignore[arg-type]

        else:
            indices = list(range(len(self.dataset)))  # type: ignore[arg-type]

        
        ## now seeing if the image data in the given batch there are even number of batches or not.
        if not self.drop_last:
            # add extra samples to make it evenly divisible
            padding_size = self.total_size - len(indices)
            if padding_size <= len(indices):
                indices += indices[:padding_size]
            else:
                indices += (indices * math.ceil(padding_size / len(indices)))[:padding_size]

        else:
            indices = indices[:self.total_size]

        assert len(indices) == self.total_size

        # subsample from current pointer ordering to the end result with the replicas being increased with num_replicas.
        indices = indices[self.rank:self.total_size:self.num_replicas]
        assert len(indices) == self.num_samples

        # assert self.start_index < len(indices)
        if self.start_index >= len(indices):
            print('(Warning): Start index is less than len of dataloader. Goint to the last batch of dataset instead')
            # This is hardcoded to go one batch before.
            self.start_index = len(indices) - 64
        indices = indices[self.start_index:]

        return iter(indices)

    def __len__(self):
        return self.num_samples

    def set_epoch(self, epoch):
        self.epoch = epoch

    def set_iteration(self, start_index):
        self.start_index = start_index
            
        
