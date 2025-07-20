import zipfile
from pathlib import Path

import lightning as L
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


class EmotionsDataModule(L.LightningDataModule):
    def __init__(self, batch_size: int = 16):
        super().__init__()
        self.batch_size = batch_size
        self.train_path = "data/emotions/train"
        self.test_path = "data/emotions/test"
        self.train_transform = transforms.Compose(
            [
                transforms.Resize(224),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]
        )
        self.test_transform = transforms.Compose(
            [
                transforms.Resize(224),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]
        )

    def prepare_data(self):
        if Path("data/emotions/").is_dir():
            return
        with zipfile.ZipFile("data/emotions.zip", "r") as zip_ref:
            zip_ref.extractall("data/emotions")

    def setup(self, stage: str):
        if stage == "fit":
            self.train_dataset = datasets.ImageFolder(
                self.train_path, transform=self.train_transform
            )
        if stage == "test":
            self.test_dataset = datasets.ImageFolder(
                self.test_path, transform=self.test_transform
            )

    def train_dataloader(self):
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=8,
            pin_memory=True,
        )

    def test_dataloader(self):
        return DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            num_workers=8,
            pin_memory=True,
        )
