import lightning as L
import mlflow
import mlflow.data.meta_dataset
import mlflow.pytorch
import numpy as np
import pendulum
import torch
from lightning.pytorch.loggers import MLFlowLogger

from src.data.emotions_dataset import EmotionsDataModule
from src.models.linear_model import LinearModel

BATCH_SIZE = 16
CLASSES = [
    "angry",
    "disgusted",
    "fearful",
    "happy",
    "neutral",
    "sad",
    "surprised",
]

if __name__ == "__main__":
    torch.set_float32_matmul_precision("medium")
    mlflow.system_metrics.enable_system_metrics_logging()
    model_signature = mlflow.models.infer_signature(
        model_input=np.random.randint(
            0, 255, (BATCH_SIZE, 3, 224, 224), dtype=np.uint8
        ),
        model_output=np.random.randint(0, 6, (BATCH_SIZE), dtype=np.int64),
    )
    logger = MLFlowLogger(
        experiment_name="EmotionsClassifier",
        tracking_uri="http://localhost:8080",
        run_name=str(pendulum.now().format("YYYYMMDD_HHmmss")),
    )
    dm = EmotionsDataModule(batch_size=BATCH_SIZE)
    dataset = mlflow.data.meta_dataset.MetaDataset()

    mlflow.pytorch.autolog(
        log_models=False,
        registered_model_name="EmotionsClassifier_LinearModel",
        checkpoint_monitor="train_loss",
    )
    model = LinearModel(
        img_dims=(224, 224, 3),
        classes=CLASSES,
        model_name="EmotionsClassifier_LinearModel",
    )
    trainer = L.Trainer(
        max_epochs=1,
        accelerator="gpu",
        devices=[0],
        logger=logger,
    )

    with mlflow.start_run(run_id=logger.run_id) as run:
        trainer.fit(model, datamodule=dm)
        trainer.test(model, datamodule=dm)
        mlflow.pytorch.log_model(
            model,
            name=model.model_name,
            registered_model_name=model.model_name,
            signature=model_signature,
            input_example=np.random.randint(0, 255, (3, 224, 224), dtype=np.uint8),
        )
