import wandb
import torch
import torchvision

from matplotlib import pyplot as plt
from torchvision.transforms import functional as torchvision_F
import numpy


def get_heatmap(gray:torch.Tensor, cmap="gray"):
    """
    color codifies the various sections of the resulting training batch of images     
    """
    color = plt.get_cmap(cmap)(gray.numpy())
    color = torch.from_numpy(color[..., :3]).permute(0, 3, 1, 2).float()  # [N,3,H,W]
    return color


def preprocess_image(images, from_range=(0, 1), cmap="gray"):
    """
    gets the image matrix and then does the transform in order to final represent as heatmap 
    of the coorelation matrix (in terms of 0,1)

    images: is the matrix representation of the given image that needs to be compared


    """
    min, max = from_range
    images = (images - min) / (max - min)
    images = images.detach().cpu().float().clamp_(min=0, max=1)
    if images.shape[1] == 1:
        images = get_heatmap(images[:, 0], cmap=cmap)
    return images

def wandb_vizualization(images, from_range=(0, 1)):
    
    """
    gets the vizualization of the training weights for each batches. 
    """
    images = preprocess_image(images, from_range=from_range)
    image_grid = torchvision.utils.make_grid(images, nrow=1, pad_value=1)
    image_grid = torchvision_F.to_pil_image(image_grid)
    wandb_image = wandb.Image(image_grid)
    return wandb_image
