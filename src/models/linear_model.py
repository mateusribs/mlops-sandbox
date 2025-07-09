import lightning as L
import torch
import torch.nn as nn
import torchmetrics
import torchmetrics.classification


class LinearModel(L.LightningModule):

    def __init__(self, img_dims: tuple, n_classes: int):
        super().__init__()
        n_features = img_dims[0] * img_dims[1] * img_dims[2]

        self.flatten = nn.Flatten()
        self.fc = nn.Linear(n_features, n_classes)
        self.loss_fn = nn.NLLLoss()

        self.train_accuracy = torchmetrics.classification.Accuracy(
            task="multiclass", num_classes=n_classes
        )
        self.test_accuracy = torchmetrics.classification.Accuracy(
            task="multiclass", num_classes=n_classes
        )
        self.save_hyperparameters()

    def forward(self, x):
        x = self.flatten(x)
        x = self.fc(x)
        x = nn.functional.softmax(x, dim=1)
        return x

    def training_step(self, batch):
        images, labels = batch
        outputs = self.forward(images)
        loss = self.loss_fn(outputs, labels)
        self.train_accuracy(outputs, labels)
        self.log("train_loss", loss, on_step=False, on_epoch=True)
        self.log("train_acc", self.train_accuracy, on_step=False, on_epoch=True)
        return loss

    def test_step(self, batch):
        images, labels = batch
        outputs = self.forward(images)
        loss = self.loss_fn(outputs, labels)
        self.test_accuracy(outputs, labels)
        self.log("test_loss", loss, on_step=False, on_epoch=True)
        self.log("test_acc", self.test_accuracy, on_step=False, on_epoch=True)
        return loss

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=1e-3)
        return optimizer
