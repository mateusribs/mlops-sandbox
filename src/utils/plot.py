import math

import matplotlib.pyplot as plt
import torch

MEAN = torch.Tensor([0.485, 0.456, 0.406])
STD = torch.Tensor([0.229, 0.224, 0.225])


def export_figure_mosaic(
    images: torch.Tensor,
    labels: torch.Tensor,
    predictions: torch.Tensor,
    classes: list[str],
) -> plt.Figure:
    num_images = images.shape[0]
    num_cols = 4
    num_rows = math.ceil(num_images / num_cols)
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(12, 3 * num_rows))
    axes = axes.flatten()

    # Vectorize tensor operations to run on the entire batch
    images = images.cpu() * STD[:, None, None] + MEAN[:, None, None]
    images = images.permute(0, 2, 3, 1)  # From NCHW to NHWC
    predicted_indices = predictions.cpu().argmax(dim=1)
    labels = labels.cpu()

    for i in range(num_images):
        ax = axes[i]
        label = classes[labels[i]]
        prediction = classes[predicted_indices[i]]

        ax.imshow(images[i])
        ax.axis("off")
        ax.set_title(f"Label: {label}\nPred: {prediction}")

    # Hide any unused subplots
    for i in range(num_images, len(axes)):
        axes[i].axis("off")

    plt.tight_layout()
    plt.close(fig)

    return fig
