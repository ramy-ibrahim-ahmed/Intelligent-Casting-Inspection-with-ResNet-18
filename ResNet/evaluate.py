import torch
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_curve,
    auc,
    confusion_matrix,
)
import seaborn as sns
import matplotlib.pyplot as plt


def evaluate(
    model,
    test_loader,
    device,
    threshold: float = 0.5,
    trial_dir=None,
    save=True,
):
    # Initialize variables for accuracy calculation and storing labels
    all_labels = []
    all_preds = []
    all_probs = []

    # Turn off gradients for evaluation
    with torch.no_grad():
        correct = 0
        total = 0
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)

            # Forward pass
            outputs = model(images)

            # Get predictions and probabilities
            probabilities = torch.sigmoid(outputs)
            predicted = (probabilities > threshold).float()

            # Accumulate total and correct counts
            total += labels.size(0)
            correct += (predicted.squeeze() == labels.float()).sum().item()

            # Store true labels, predictions, and probabilities for metrics
            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(predicted.cpu().numpy())
            all_probs.extend(probabilities.cpu().numpy())

            del images, labels, outputs

    # Compute accuracy
    accuracy = 100 * correct / total
    print(f"Accuracy of the network on the {total} test images: {accuracy:.2f}%")

    # Compute precision, recall, and F1 score
    precision = precision_score(all_labels, all_preds)
    recall = recall_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds)  # F1 score
    print(f"Precision: {precision:.4f}, Recall: {recall:.4f}, F1 Score: {f1:.4f}")

    # Compute confusion matrix
    cm = confusion_matrix(all_labels, all_preds)

    # Compute ROC curve and AUC
    fpr, tpr, _ = roc_curve(all_labels, all_probs)
    roc_auc = auc(fpr, tpr)

    # Create a single figure with subplots
    _, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Plot confusion matrix
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cbar=False,
        xticklabels=["Ok", "Defective"],
        yticklabels=["Ok", "Defective"],
        ax=axes[0],
        linewidths=0.5,
    )
    axes[0].set_title("Confusion Matrix")
    axes[0].set_xlabel("Predicted")
    axes[0].set_ylabel("True")

    # Plot ROC curve
    axes[1].plot(fpr, tpr, color="black", label=f"ROC Curve (AUC = {roc_auc:.4f})")
    axes[1].plot([0, 1], [0, 1], color="gray", linestyle="--")
    axes[1].set_title("ROC Curve")
    axes[1].set_xlabel("False Positive Rate")
    axes[1].set_ylabel("True Positive Rate")
    axes[1].legend(loc="lower right")
    axes[1].grid(True, lw=0.5, linestyle="--")

    # Adjust layout and save the figure
    plt.tight_layout()
    if save:
        plt.savefig(f"{trial_dir}/roc_and_confusion_th={threshold}.png")
    plt.show()
