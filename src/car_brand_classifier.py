"""
Car Brands Classifier (Developing)
A neural network model that identifies car brands from images.
"""

from __future__ import annotations

import os
import torch
import torch_directml
import torch.nn as nn
import torch.optim as optim
from torchvision import models
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader
import scipy.io
import logging
from PIL import Image
import matplotlib.pyplot as plt

# ==============================================================================
# Constants
# ==============================================================================

DATA_DIRECTORY = '../data/Stanford_Cars/'
BATCH_SIZE = 32
NUM_BRANDS = 49
NUM_EPOCHS = 10
MODEL_FILE_NAME = 'car_brand_classifier.pth'

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
        #'fname' is numpy, convert to string, also remove '[] symbols from name
        img_fname = str(self.annos[idx]['fname']).translate(str.maketrans('','',"'[]"))

        try:
            img = Image.open(DATA_DIRECTORY+'cars_train/' + img_fname).convert("RGB")
        except Exception:
            logging.error(f"Image not found or failed to load: {DATA_DIRECTORY+'cars_train/' + img_fname}")
            return None
        
        transformed_img = self.transform(img)
        return transformed_img, int(self.annos[idx]['class'][0][0])



# ==============================================================================
# AI Model
# ==============================================================================

# We use resnet18 for faster processing
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
# Replace final layer for number of brands
model.fc = nn.Linear(model.fc.in_features, NUM_BRANDS)
# Enable each parameter to be trainable
for parameter in model.fc.parameters():
    parameter.requires_grad = True
# GPU, Loss Function and Optimizer
dml_device = torch_directml.device()
model.to(dml_device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.01)



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



def model_training(training_loader) -> None:
    for epoch in range(NUM_EPOCHS):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        for images, labels in training_loader:

            images, labels = images.to(dml_device), labels.to(dml_device)
            optimizer.zero_grad()
            outputs = model(images)

            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        logging.info(f"Epoch {epoch+1}, Loss: {running_loss/len(training_loader):.4f}, Accuracy: {100*correct/total:.2f}%")
    torch.save(model.state_dict(), MODEL_FILE_NAME)
            

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

    training_dataset = CarDataSet(train_annos, transform, brand_list)
    training_loader = DataLoader(training_dataset, batch_size=BATCH_SIZE, shuffle=True)
    #randomize order and use BATCH_SIZE at once
    print(brand_list)
    choice = input("Do you wanna train a model?")
    if (choice == 'y'):
        model_training(training_loader)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted - exiting.")