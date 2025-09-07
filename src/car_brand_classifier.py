"""
Car Brands Classifier (Developing)
A neural network model that identifies car brands from images.
"""

from __future__ import annotations

import os
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import scipy.io
import logging
from PIL import Image
import matplotlib.pyplot as plt

# ==============================================================================
# Constants
# ==============================================================================

DATA_DIRECTORY = '../data/Stanford_Cars/'

# ==============================================================================
# Logging
# ==============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)

# ==============================================================================
# Dataset class
# ==============================================================================

class CarDataSet(Dataset):
    def __init__(self, annos, transform=None, brands=None):
        self.annos = annos
        self.transform = transform
        self.brands = brands

    def __len__(self):
        return len(self.annos)
    def __getitem__(self, idx):
        img_fname = str(self.annos[idx]['fname']).translate(str.maketrans('','',"'[]"))
        #'fname' is numpy, convert to string, also remove '[] symbols from name
        try:
            img = Image.open(DATA_DIRECTORY+'cars_train/' + img_fname).convert("RGB")
        except Exception:
            logging.error(f"Image not found or failed to load: {DATA_DIRECTORY+'cars_train/' + img_fname}")
            return None
        transformed_img = self.transform(img)
        return transformed_img, self.annos[idx]['class']



# ==============================================================================
# Core Functions
# ==============================================================================

def load_dataset() -> dict:
    if (os.path.exists(DATA_DIRECTORY+'car_devkit/devkit/cars_meta.mat') and os.path.exists(DATA_DIRECTORY+'car_devkit/devkit/cars_train_annos.mat')):
        logging.info(f"Loading data...")  
        meta = scipy.io.loadmat(DATA_DIRECTORY + 'car_devkit/devkit/cars_meta.mat')['class_names'][0] #size=(,196)
        train_annos = scipy.io.loadmat(DATA_DIRECTORY + 'car_devkit/devkit/cars_train_annos.mat')['annotations'][0] #size=(,8144)
        brand_list = {}
        for i, name in enumerate(meta):
            brand = name[0].split()[0]   #"Tesla Model Y" -> "Tesla"
            if brand not in brand_list:
                brand_list[brand] = []
            brand_list[brand].append(i) #Mapping between the car brands and class id
    else:
        logging.error("Error: Required .mat files not found.")
        return {}
    return brand_list, train_annos


# ==============================================================================
# Main Program
# ==============================================================================

def main() -> None:
    brand_list, train_annos = load_dataset()  
    #print(brand_list)
    #print(train_annos[1]['fname'])
    transform = transforms.Compose([
        transforms.Resize([256,256]),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.ToTensor(),    #PyTorch tensor object
        transforms.Normalize(mean=[0.5], std=[0.5])
    ])
    cars = CarDataSet(train_annos, transform, brand_list)
    print(cars[1])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted - exiting.")