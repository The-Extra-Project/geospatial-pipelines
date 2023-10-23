import importlib
import json
import os
import threading
import time
import wandb
from tqdm import tqdm
import inspect


import torch
from torch.autograd import profiler
from torch.cuda.amp import GradScaler, autocast_mode

from neuralangelo_modified.utils.misc import get_train_dataloader, get_val_dataloader, get_test_dataloader, wrap_model, get_trainers, requires_grad, to_cpu, to_cuda, set_random_seed, cal_model_parameters

from neuralangelo_modified.model.base import weights_init, weights_rescale
from neuralangelo_modified.utils.config import Timer, Model, CheckPointer
from neuralangelo_modified.utils.gpu_jobs import master_only_print, master_only, is_master, get_optimizer, get_scheduler



class BaseTrainer(object):
    r"""Base trainer. We expect that all trainers inherit this class.

    Args:
        cfg (obj): Global configuration.
        is_inference (bool): if True, load the test dataloader and run in inference mode.
    """

    def __init__(self, cfg, is_inference=True, seed=0):
        super().__init__()
        print('started training on master {}'.format(is_master()))
        self.cfg = cfg
        torch.cuda.set_device(self.cfg.local_rank)
        if not is_inference:
            self.optim = self.setup_optimizer(cfg, self.model, seed=seed)
            self.sched = self.setup_scheduler(cfg, self.optim)
        else:
            self.optim = None
            self.sched = None
        
        self.model = wrap_model(cfg, seed=seed)
        self.is_inference = is_inference
        self.init_amp()

        # Initialize loss functions.
        self.init_losses(cfg)


        self.checkpointer = CheckPointer(cfg, self.model, self.optim, self.sched)
        self.timer = Timer(cfg)
        
        ## these steps are not required post inference 
        if self.is_inference:
            return
        self.current_iteration = 0
        self.current_epoch = 0
        self.start_iteration_time = None
        self.start_epoch_time = None
        self.elapsed_iteration_time = 0
        if self.cfg.speed_benchmark:
            self.timer.reset()
        if self.cfg.metrics_iter is None:
            self.cfg.metrics_iter = self.cfg.checkpoint.save_iter
        if self.cfg.metrics_epoch is None:
            self.cfg.metrics_epoch = self.cfg.checkpoint.save_epoch

        # defining the instance (either the pytorch enabled AWS / CGP instance or the bacalhau ones)
        # TODO: need to confgure and support the bacalhau instance
        if hasattr(cfg, 'aws_credentials_file'):
            with open(cfg.aws_credentials_file) as fin:
                self.credentials = json.load(fin)
        else:
            self.credentials = None
        if 'TORCH_HOME' not in os.environ:
            os.environ['TORCH_HOME'] = os.path.join(os.environ['HOME'], ".cache")

        
    def set_data_loader(self, cfg, split, shuffle=True, drop_last=True, seed=0):
        """Set the data loader corresponding to the share of training , test and eval data shards.
        Args:
            split (str): Must be either 'train', 'val', or 'test'.
            shuffle (bool): Whether to shuffle the data (only applies to the training set).
            drop_last (bool): Whether to drop the last batch if it is not full (only applies to the training set).
            seed (int): Random seed.
        """
        assert (split in ["train", "val", "test"])
        if split == "train":
            self.train_data_loader = get_train_dataloader(cfg, shuffle=shuffle, drop_last=drop_last, seed=seed)
        elif split == "val":
            self.eval_data_loader = get_val_dataloader(cfg, seed=seed)
        elif split == "test":
            self.eval_data_loader = get_test_dataloader(cfg)
     
    def setup_model(self, cfg, seed=0):
        r""" initialize the training cluster (either on the bacalhau cluster or on the centralised one) in start they've similar number of network weights.
        with each of the GPU node is assigned different initial parameters , based on their training results from the same backprop training , the weight are aggregated 
        and then weighted moving avg algorithm is applied.
    
        The following objects are constructed as class members:
          - model (obj): Model object (historically: generator network object).

        Args:
            cfg (obj): Global configuration.
            seed (int): Random seed.
        """
        
        set_random_seed(seed)
        
        ## init network
        
        model_import = importlib.import_module(cfg.model.type)
        model: Model  = model_import.Model(cfg.model, cfg.data)
        print("the initial params are {}, with gain : {} and type : {}".format(cal_model_parameters(model), cfg.init.gain.type, cfg.trainer.init.gain))
        init_bias, init_gain = (getattr(cfg.trainer.init, 'bias', None), cfg.trainer.init.gain or 1)
        model.apply(weights_rescale(cfg.trainer.init.type, init_gain, init_bias))
        model.apply(weights_rescale())
        
        model = model.to('cuda')

        #instantiating the random parameters based of each of the initialized values.
        set_random_seed(seed, by_rank=True)
        return model
    
    
    def setup_optimizer(self,cfg_optim, model: Model, seed=0):
        r""" aggregates  the optimizer object. 
        
        Args:
            cfg_optim(obj): gets the global configuration of the optimizers (individual/idstributed).
            model: the wrapped implementation of torch module for whom you need to get the parameters
            seed: is the random association of the parameters to the various GPU nodes.
    
        """
        
        
        optim = get_optimizer(cfg_optim, model)
        if 'set_to_none' in inspect.signature(cfg_optim.zero_grad).parameters:
            self.optim_zero_grad_kwargs['set_to_none'] = True
        return optim
    
    def setup_scheduler(self, cfg, optim):
        r"""Return the schedulers.

        The following objects are constructed as class members:
          - sched (obj): Model optimizer scheduler object.

        Args:
            cfg (obj): Global configuration.
        """
        return get_scheduler(cfg.optim, optim)