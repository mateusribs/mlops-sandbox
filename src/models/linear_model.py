import lightning as L
import torch
import torch.nn as nn
import torchmetrics
import torchmetrics.classification

from src.utils.plot import export_figure_mosaic


class LinearModel(L.LightningModule):

    def __init__(self, img_dims: tuple, classes: list[str], model_name: str):
        super().__init__()
        self.classes = classes
        self.model_name = model_name
        n_features = img_dims[0] * img_dims[1] * img_dims[2]
        n_classes = len(classes)

        self.flatten = nn.Flatten()
        self.fc = nn.Linear(n_features, n_classes)
        self.loss_fn = nn.NLLLoss()

        self.train_accuracy = torchmetrics.classification.Accuracy(
            task="multiclass", num_classes=n_classes
        )
        self.test_accuracy = torchmetrics.classification.Accuracy(
            task="multiclass", num_classes=n_classes
        )
        self.cm = torchmetrics.classification.MulticlassConfusionMatrix(
            num_classes=n_classes
        ).to("cpu")
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
        self.log_dict(
            {
                "train_loss": loss,
                "train_acc": self.train_accuracy,
            },
            on_step=False,
            on_epoch=True,
        )
        self.logger.experiment
        return loss

    def test_step(self, batch):
        images, labels = batch
        outputs = self.forward(images)
        loss = self.loss_fn(outputs, labels)
        self.test_accuracy(outputs, labels)
        self.log_dict(
            {
                "test_loss": loss,
                "test_acc": self.test_accuracy,
            },
            on_step=False,
            on_epoch=True,
        )

        return {
            "test_loss": loss,
            "test_acc": self.test_accuracy,
            "predictions": outputs,
        }

    def on_test_batch_end(self, outputs, batch, batch_idx, dataloader_idx=0):

        if batch_idx % 50 != 0:
            return

        images, labels = batch
        self.cm.update(
            outputs["predictions"].argmax(dim=1),
            labels,
        )
        figure = export_figure_mosaic(
            images, labels, outputs["predictions"], self.classes
        )
        self.logger.experiment.log_figure(
            figure=figure,
            artifact_file=f"test_batch_{batch_idx}.png",
            run_id=self.logger.run_id,
        )

    def on_test_end(self):
        fig, ax = self.cm.plot(cmap="viridis", labels=self.classes)
        self.logger.experiment.log_figure(
            figure=fig, artifact_file=f"confusion_matrix.png", run_id=self.logger.run_id
        )

    def configure_optimizers(self):
        self.logger.log_hyperparams({"lr": 1e-3, "optimizer": "Adam"})
        optimizer = torch.optim.Adam(self.parameters(), lr=1e-3)
        return optimizer
