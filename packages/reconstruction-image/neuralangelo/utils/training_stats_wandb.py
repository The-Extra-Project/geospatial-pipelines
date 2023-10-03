import math
import wandb
import torch
from torch.utils.tensorboard import SummaryWriter
from torch import Tensor
from utils.gpu_jobs import master_only

## global variables defining the URI of the stored results 
"""
Consist of helper functions in order to display the training results of the model on wandb / tensorboard.
"""

class TrainingStats():
    Log_dir: str
    Log_writer: SummaryWriter
    def __init__(self, log_dir):
        self.Log_dir = log_dir
    
    @master_only
    def setup_tensorboard(self):
        self.Log_writer = SummaryWriter(log_dir=self.Log_dir)
   

    @torch.no_grad()
    def reshape_weight_to_matrix(weight_params: Tensor):
     """
     organizes the matrix with column dimensions
     
     """
     return weight_params.reshape(weight_params.size(0), -1)
 
 
    @torch.no_grad()
    def get_weight_stats(self,mod):
        r"""Get weight state

        Args:
            mod: Pytorch module of neuralangelo whose training result is to be shown
        """
        if mod.weight_orig.grad is not None:
            grad_norm = mod.weight_orig.grad.data.norm().item()
        else:
            grad_norm = 0.
            weight_norm = mod.weight_orig.data.norm().item()
            weight_mat = self.reshape_weight_to_matrix(mod.weight_orig)
            sigma = torch.sum(mod.weight_u * torch.mv(weight_mat, mod.weight_v))
        return grad_norm, weight_norm, sigma


    def log_tensorboard_result(self,name, summary, step, history=False):
        r"""
    log directory of each epoch training results are stored
        args:
        name: str : defines the title of the given model training session
        summary: is the tensor result corresponding to the given training session
        step: is the information to the given 
        TODO: needs to add another function to access those results if they are done on distributed computing 
        """
        if self.Log_writer is None:
            raise Exception("needs to set the tensorboard in order to fetch the result")
        if history:
            self.Log_writer.add_histogram(tag=name, values=summary, global_step=step)
            
        else:
            ## its adding only for one step, and thus being the single input
            self.Log_writer.add_scalar(tag=name, values=summary, global_step=step)
    
    
    
