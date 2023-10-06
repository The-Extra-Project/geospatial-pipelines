"""
this file consist of utility functions to parse the training parameters and the training architecture of the model
"""


import collections
import functools
import os
import re
import signal
import torch
import time
import yaml
import copy
from torch import nn

## flag set for defining the logging level
DEBUG = False

from neuralangelo_modified.utils.gpu_jobs import master_print as print, master_only, is_master
from neuralangelo_modified.utils.misc import alarm_handler, requires_grad

from torch.nn import init
import math
import pynvml
import wandb

class yamlConfigParser(dict):
    """
    base class takes the tuple of key (represented by the name of the parameter by the inheriting class) and the corresponding value of the configuration
    stored in the yaml configuration fille.
    
    """
    
    
    def __init__(self, *args, **kwargs):
        super(yamlConfigParser, self).__init__(*args, **kwargs)
        self.__dict__ = self
        for key, value in self.__dict__.items():
            if isinstance(value, dict):
                self.__dict__[key] = yamlConfigParser(value)
            elif isinstance(value, (list, tuple)):
                if value and isinstance(value[0], dict):
                    self.__dict__[key] = [yamlConfigParser(item) for item in value]
                else:
                    self.__dict__[key] = value

    
    def toYaml(self):
        """converts the given config parser object to a yaml dictionary"""
        yaml_dict = {}
        for key, value in self.__dict__.items():
            if isinstance(value, yamlConfigParser):
                yaml_dict[key] = value.yaml()
            elif isinstance(value, list):
                if value and isinstance(value[0], yamlConfigParser):
                    new_l = []
                    for item in value:
                        new_l.append(item.yaml())
                    yaml_dict[key] = new_l
                else:
                    yaml_dict[key] = value
            else:
                yaml_dict[key] = value
        return yaml_dict

    
    def __repr__(self):
        """
        print all the configuration variables formatted from yaml file (it overrides the standard class object).
        """     
        ret_str = []
        for key, value in self.__dict__.items():
            if isinstance(value, yamlConfigParser):
                ret_str.append('{}:'.format(key))
                child_ret_str = value.__repr__().split('\n')
                for item in child_ret_str:
                    ret_str.append('    ' + item)
            elif isinstance(value, list):
                if value and isinstance(value[0], yamlConfigParser):
                    ret_str.append('{}:'.format(key))
                    for item in value:
                        # Treat as yamlConfigParser above.
                        child_ret_str = item.__repr__().split('\n')
                        for item in child_ret_str:
                            ret_str.append('    ' + item)
                else:
                    ret_str.append('{}: {}'.format(key, value))
            else:
                ret_str.append('{}: {}'.format(key, value))
        return '\n'.join(ret_str)





class Config(yamlConfigParser):
    r""" stores all the model training parameters defined in the [neuralangelo_modified/neuralangelo_config.yaml] file.
    """
    
    def __init__(self, filename=None, verbose=False):
        super(Config, self).__init__()
        self.source_filename = filename

        # Load the base configuration file.
        base_filename = os.path.join(
            os.path.dirname(__file__), '../neuralangelo_conda_deps.yaml'
        )
        
        cfg_base = self.load_config(base_filename)
        recursive_update(self, cfg_base)

        # Update with given configurations and print them
        cfg_dict = self.load_config(filename)
        recursive_update(self, cfg_dict)
    
        if verbose:
            print(' neuralangelo training config '.center(80, '-'))
            print(self.__repr__())
            print(''.center(80, '-'))
            
    
    
    def load_config(self, filename):
        # Update with given configurations.
        assert os.path.exists(filename), f'File {filename} not exist.'
        yaml_loader = yaml.SafeLoader
        yaml_loader.add_implicit_resolver(
            u'tag:yaml.org,2002:float',
            re.compile(u'''^(?:
             [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
            |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
            |\\.[0-9_]+(?:[eE][-+][0-9]+)?
            |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*
            |[-+]?\\.(?:inf|Inf|INF)
            |\\.(?:nan|NaN|NAN))$''', re.X),
            list(u'-+0123456789.'))
        try:
            with open(filename) as file:
                cfg_dict = yaml.load(file, Loader=yaml_loader)
                cfg_dict = yamlConfigParser(cfg_dict)
        except EnvironmentError:
            print(f'Please check the file with name of "{filename}"')
        # Inherit configurations from parent
        parent_key = "_parent_"
        if parent_key in cfg_dict:
            parent_filename = cfg_dict.pop(parent_key)
            cfg_parent = self.load_config(parent_filename)
            recursive_update(cfg_parent, cfg_dict)
            cfg_dict = cfg_parent
        return cfg_dict

    def print_config(self, level=0):
        """Recursively print the configuration (with termcolor)."""
        for key, value in sorted(self.items()):
            if isinstance(value, (dict, Config)):
                print("   " * level + "* " + key + ":")
                Config.print_config(value, level + 1)
            else:
                print("   " * level + "* " + (key) + ":", (value))

    def save_config(self, logdir):
        """Save the final configuration to a yaml file."""
        cfg_fname = f"{logdir}/config.yaml"
        with open(cfg_fname, "w") as file:
            yaml.safe_dump(self.yaml(), file, default_flow_style=False, indent=4)

            
    

    
    
def recursive_update(self, current_dict, update):
    """
        Updates the current state of the configuration with that of the updated tuple 'update'
    """
    for key, value in update.items():
        if isinstance(value, collections.abc.Mapping):
            current_dict.__dict__[key] = recursive_update(current_dict.get(key, yamlConfigParser({})), value)
        elif isinstance(value, (list, tuple)):
            if value and isinstance(value[0], dict):
                current_dict.__dict__[key] = [yamlConfigParser(item) for item in value]
            else:
                current_dict.__dict__[key] = value
        else:
            current_dict.__dict__[key] = value
    return current_dict

    

def recursive_update_strict(dictionary: dict, update, stack= []):
    """
    updated version of the recursive matching with the condition that if the current key from the update is not in the dictionary, 
    it will not update.
    dictionary: current state of the dictionary (storing the command strings/ arguments for eg)
    
    
        
    """
    
    for key,value in update.items():
        if isinstance(value, collections.abc.Mapping):
            if key not in dictionary:
                key_str = '.'.join(stack + [key])
                raise KeyError(f"The input parameter name (key) '{key_str}; does not exist in the config files.")
            if isinstance(value, collections.abc.Mapping):
                dictionary.__dict__[key] = recursive_update_strict(dictionary.get(key, yamlConfigParser({})), value, stack + [key])

        
        elif isinstance(value, (list, tuple)):
            if value and isinstance(value[0], dict):
                dictionary.__dict__[key] = [yamlConfigParser(item) for item in value]
            else:
                dictionary.__dict__[key] = value
        else:
            dictionary.__dict__[key] = value


def rsetattr(obj, attr, val):
    """Recursively find object and set value"""
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


def rgetattr(obj, attr, *args):
    """Recursively find object and return value"""

    def _getattr(obj, attr):
        r"""Get attribute."""
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split('.'))


        
## details about the gpu driver association.

class Device(object):
    r"""Device used for nvml."""
    _nvml_affinity_elements = math.ceil(os.cpu_count() / 64)

    def __init__(self, device_idx):
        super().__init__()
        self.handle = pynvml.nvmlDeviceGetHandleByIndex(device_idx)

    def get_name(self):
        r"""Get obect name"""
        return pynvml.nvmlDeviceGetName(self.handle)

    def get_cpu_affinity(self):
        r"""Get CPU affinity"""
        affinity_string = ''
        for j in pynvml.nvmlDeviceGetCpuAffinity(self.handle, Device._nvml_affinity_elements):
            # assume nvml returns list of 64 bit ints
            affinity_string = '{:064b}'.format(j) + affinity_string
        affinity_list = [int(x) for x in affinity_string]
        affinity_list.reverse()  # so core 0 is in 0th element of list

        return [i for i, e in enumerate(affinity_list) if e != 0]

class Timer(object):

    def __init__(self, cfg):
        self.cfg = cfg
        self.time_iteration = 0
        self.time_epoch = 0
        if is_master():
            # noinspection PyTypeChecker
            signal.signal(signal.SIGALRM, functools.partial(alarm_handler, self.cfg.timeout_period))

    def reset(self):
        self.accu_forw_iter_time = 0
        self.accu_loss_iter_time = 0
        self.accu_back_iter_time = 0
        self.accu_step_iter_time = 0
        self.accu_avg_iter_time = 0

    def _time_before_forward(self):
        r"""Record time before applying forward."""
        if self.cfg.speed_benchmark:
            torch.cuda.synchronize()
            self.forw_time = time.time()

    def _time_before_loss(self):
        r"""Record time before computing loss."""
        if self.cfg.speed_benchmark:
            torch.cuda.synchronize()
            self.loss_time = time.time()

    def _time_before_backward(self):
        r"""Record time before applying backward."""
        if self.cfg.speed_benchmark:
            torch.cuda.synchronize()
            self.back_time = time.time()

    def _time_before_step(self):
        r"""Record time before updating the weights"""
        if self.cfg.speed_benchmark:
            torch.cuda.synchronize()
            self.step_time = time.time()

    def _time_before_model_avg(self):
        r"""Record time before applying model average."""
        if self.cfg.speed_benchmark:
            torch.cuda.synchronize()
            self.avg_time = time.time()

    def _time_before_leave_gen(self):
        r"""Record forward, backward, loss, and model average time for the network update."""
        if self.cfg.speed_benchmark:
            torch.cuda.synchronize()
            end_time = time.time()
            self.accu_forw_iter_time += self.loss_time - self.forw_time
            self.accu_loss_iter_time += self.back_time - self.loss_time
            self.accu_back_iter_time += self.step_time - self.back_time
            self.accu_step_iter_time += self.avg_time - self.step_time
            self.accu_avg_iter_time += end_time - self.avg_time

    def _print_speed_benchmark(self, avg_time):
        """Prints the profiling results and resets the timers."""
        print('{:6f}'.format(avg_time))
        print('\tModel FWD time {:6f}'.format(self.accu_forw_iter_time / self.cfg.logging_iter))
        print('\tModel LOS time {:6f}'.format(self.accu_loss_iter_time / self.cfg.logging_iter))
        print('\tModel BCK time {:6f}'.format(self.accu_back_iter_time / self.cfg.logging_iter))
        print('\tModel STP time {:6f}'.format(self.accu_step_iter_time / self.cfg.logging_iter))
        print('\tModel AVG time {:6f}'.format(self.accu_avg_iter_time / self.cfg.logging_iter))
        self.accu_forw_iter_time = 0
        self.accu_loss_iter_time = 0
        self.accu_back_iter_time = 0
        self.accu_step_iter_time = 0
        self.accu_avg_iter_time = 0

    def checkpoint_tic(self):
        # reset timer
        self.checkpoint_start_time = time.time()

    def checkpoint_toc(self):
        # return time by minutes
        return (time.time() - self.checkpoint_start_time) / 60

    @master_only
    def reset_timeout_counter(self):
        signal.alarm(self.cfg.timeout_period)



class Model(torch.nn.Module):
    def __init__(self, cfg_model, cfg_data):
        super().__init__()

    def get_param_groups(self, cfg_optim):
        """Allow the network to use different hyperparameters (e.g., learning rate) for different parameters.
        Returns:
            PyTorch parameter group (list or generator). See the PyTorch documentation for details.
        """
        return self.parameters()

    def device(self):
        """Return device on which model resides."""
        return next(self.parameters()).device


class WrappedModel():
    """
    provides wrapper functions on top of pytorch forward training function.
    its used in case id the training is not distributed
    """
    def __init__(self, module):
        super(WrappedModel, self).__init__()
        self.module = module

    def forward(self, *args, **kwargs):
        r"""PyTorch module forward function overload."""
        return self.module(*args, **kwargs)


class ModelAverage(nn.Module):
    r"""In this model average implementation, the spectral layers are
    absorbed in the model parameter by default. If such options are
    turned on, be careful with how you do the training. Remember to
    re-estimate the batch norm parameters before using the model.

    Args:
        module (torch nn module): Torch network.
        beta (float): Moving average weights. How much we weight the past.
        start_iteration (int): From which iteration, we start the update.
    """
    def __init__(self, module, beta=0.9999, start_iteration=0):
        super(ModelAverage, self).__init__()

        self.module = module
        # A shallow copy creates a new object which stores the reference of
        # the original elements.
        # A deep copy creates a new object and recursively adds the copies of
        # nested objects present in the original elements.
        self._averaged_model = copy.deepcopy(self.module).to('cuda')
        self.stream = torch.cuda.Stream()

        self.beta = beta

        self.start_iteration = start_iteration
        # This buffer is to track how many iterations has the model been
        # trained for. We will ignore the first $(start_iterations) and start
        # the averaging after.
        self.register_buffer('num_updates_tracked',
                             torch.tensor(0, dtype=torch.long))
        self.num_updates_tracked = self.num_updates_tracked.to('cuda')
        self.averaged_model.eval()

        # Averaged model does not require grad.
        requires_grad(self.averaged_model, False)

    @property
    def averaged_model(self):
        self.stream.synchronize()
        return self._averaged_model

    def forward(self, *inputs, **kwargs):
        r"""PyTorch module forward function overload."""
        return self.module(*inputs, **kwargs)

    @torch.no_grad()
    def update_average(self):
        r"""Update the moving average."""
        self.stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(self.stream):
            self.num_updates_tracked += 1
            if self.num_updates_tracked <= self.start_iteration:
                beta = 0.
            else:
                beta = self.beta
            source_dict = self.module.state_dict()
            target_dict = self._averaged_model.state_dict()
            source_list = []
            target_list = []
            for key in target_dict:
                if 'num_batches_tracked' in key:
                    continue
                source_list.append(source_dict[key].data)
                target_list.append(target_dict[key].data.float())

            torch._foreach_mul_(target_list, beta)
            torch._foreach_add_(target_list, source_list, alpha=1 - beta)

    def __repr__(self):
        r"""Returns a string that holds a printable representation of an
        object"""
        return self.module.__repr__()
    
from torch.utils.data import sampler
