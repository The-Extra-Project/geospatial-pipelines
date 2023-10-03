"""

addition util and inheritable functions for training the model

Credits to nvidia implementation of [neuralangelo](https://github.com/NVlabs/neuralangelo).

"""
import torch
from torch.nn import init
from torch import nn
from utils.misc import requires_grad
import copy


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


## functions for initializing the weights

def weights_init(init_type: str, gain, bias=None):
    """
    initializing the weights in the network
    init_type(str): defines the type of initialization techniques
    gain:  corresponding value for the initialization technique
    bias(Object): defines the bias value, by default its None that defines for the initialization.
    
    returns:        
    (obj): init function to be applied
    """
    
    def init_func(m):
        r"""Init function

        Args:
            m: module to be weight initialized.
        """
        class_name = m.__class__.__name__
        if hasattr(m, 'weight') and (
                class_name.find('Conv') != -1 or
                class_name.find('Linear') != -1 or
                class_name.find('Embedding') != -1):
            lr_mul = getattr(m, 'lr_mul', 1.)
            gain_final = gain / lr_mul
            if init_type == 'normal':
                init.normal_(m.weight.data, 0.0, gain_final)
            elif init_type == 'xavier':
                init.xavier_normal_(m.weight.data, gain=gain_final)
            elif init_type == 'xavier_uniform':
                init.xavier_uniform_(m.weight.data, gain=gain_final)
            elif init_type == 'kaiming':
                init.kaiming_normal_(m.weight.data, a=0, mode='fan_in')
                with torch.no_grad():
                    m.weight.data *= gain_final
            elif init_type == 'kaiming_linear':
                init.kaiming_normal_(
                    m.weight.data, a=0, mode='fan_in', nonlinearity='linear'
                )
                with torch.no_grad():
                    m.weight.data *= gain_final
            elif init_type == 'orthogonal':
                init.orthogonal_(m.weight.data, gain=gain_final)
            elif init_type == 'none':
                pass
            else:
                raise NotImplementedError(
                    'initialization method [%s] is '
                    'not implemented' % init_type)
        if hasattr(m, 'bias') and m.bias is not None:
            if init_type == 'none':
                pass
            elif bias is not None:
                bias_type = getattr(bias, 'type', 'normal')
                if bias_type == 'normal':
                    bias_gain = getattr(bias, 'gain', 0.5)
                    init.normal_(m.bias.data, 0.0, bias_gain)
                else:
                    raise NotImplementedError(
                        'initialization method [%s] is '
                        'not implemented' % bias_type)
            else:
                init.constant_(m.bias.data, 0.0)
    return init_func


def weights_rescale():
    """
    function for scaling the weights based on the initialization parameters

    """
    def init_func(m):
        if hasattr(m, 'init_gain'):
            for name, p in m.named_parameters():
                if 'output_scale' not in name:
                    p.data.mul_(m.init_gain)
    return init_func


class ModelAverage():
    """
       Implements the moving average of the model parameters in order to stablize the model
       it gets the weighted average of the current parameters and the moving average of the previous paraemters in the epoch (in the given window).
    
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
    
    
    
    