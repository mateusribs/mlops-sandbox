import lightning as L
from lightning.pytorch.loggers import MLFlowLogger
from data.emotions_dataset import EmotionsDataModule
from models.linear_model import LinearModel

BATCH_SIZE = 16
CLASSES_NAMES = [
    "angry",
    "disgusted",
    "fearful",
    "happy",
    "neutral",
    "sad",
    "surprised",
]

if __name__ == "__main__":
    logger = MLFlowLogger(experiment_name="emotions_classification", tracking_uri="file:./mlruns")
    dm = EmotionsDataModule(batch_size=BATCH_SIZE)
    model = LinearModel(img_dims=(224, 224, 3), n_classes=len(CLASSES_NAMES))
    trainer = L.Trainer(
        max_epochs=10, accelerator="gpu", devices=[0], default_root_dir="weights", logger=logger
    )
    trainer.fit(model, datamodule=dm)
    trainer.test(model, datamodule=dm)
