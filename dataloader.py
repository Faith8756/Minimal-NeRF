import os 
import torch 
from torch.utils.data import Dataset, DataLoader
import numpy as np
from PIL import Image
import json
import cv2

"""Utility functions are repurposed from code written by Chris Xie. 
"""

def image_to_tensor(image):
    if image.ndim == 4: # NHWC
        tensor = torch.from_numpy(image).permute(0,3,1,2).float()
    elif image.ndim == 3: # HWC
        tensor = torch.from_numpy(image).permute(2,0,1).float()
    return tensor

def worker_init_fn(worker_id):
    """ Use this to bypass issue with PyTorch dataloaders using deterministic RNG for Numpy
        https://github.com/pytorch/pytorch/issues/5059
    """
    np.random.seed(np.random.get_state()[1][0] + worker_id)

class SyntheticDataset(Dataset):

    def __init__(self, base_dir): 
        self.base_dir = base_dir
        file = open(self.base_dir)
        self.data = json.load(file)
        self.camera_angle = self.data['camera_angle_x']
        self.frames = self.data['frames']

    def __len__(self):
        return len(self.frames)

    def __getitem__(self, idx):
        return 


class PhotoDataset(Dataset):

    def __init__(self, im_path): 
        self.im_path = im_path
        im = np.array(Image.open(im_path)) / 255.0
        self.im = image_to_tensor(im) # C x H x W
        self.C, self.H, self.W = self.im.shape 

    def __len__(self):
        return self.H * self.W

    def __getitem__(self, idx):
        h = idx // self.W
        w = idx % self.W
        coords = torch.FloatTensor([h / (self.H - 1), w / (self.W - 1)])
        rgb = self.im[:, h, w]
        return coords, rgb

def getPhotoDataloader(im_path, batch_size=1024, num_workers=4, shuffle=True): 
    dataset = PhotoDataset(im_path)
    return DataLoader(dataset=dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers)

class ValDataset(Dataset):

    def __init__(self, im_path):
        self.im_path = im_path
        self.im = np.array(Image.open(im_path)) / 255.0
        self.H, self.W, self.C = self.im.shape 

    def __len__(self):
        return 1
    
    def __getitem__(self, idx):
        return (self.H, self.W)

def getValDataloader(im_path, batch_size=1, num_workers=1, shuffle=False): 
    dataset = ValDataset(im_path)
    return DataLoader(dataset=dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers)
