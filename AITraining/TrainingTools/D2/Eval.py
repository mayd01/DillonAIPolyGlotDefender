import numpy as np
import tensorflow as tf
from tensorflow import keras
import pickle
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split

def load_preprocessed_data(file_path):
    """Load preprocessed dataset from a pickle file."""
    with open(file_path, "rb") as f:
        return pickle.load(f)

print("Loading preprocessed dataset...")
X_padded, y, _ = load_preprocessed_data("/data/processed/preprocessed_data.pkl")
print("Dataset loaded.")
print(f"Total dataset size: {len(X_padded)}")

# Load the trained model
model = keras.models.load_model("polyglot_cnn_detector_best.h5")
print("Model loaded.")

# Split data into training and testing sets
_, X_test, _, y_test = train_test_split(X_padded, y, test_size=0.2, random_state=42)

# Ensure y_test is in the correct format
y_test = np.array(y_test, dtype=np.float32).reshape(-1)

# Make predictions
print("Evaluating model...")
y_pred_probs = model.predict(X_test)
y_pred = (y_pred_probs > 0.5).astype(int).reshape(-1)

# Compute evaluation metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)
report = classification_report(y_test, y_pred)

# Print evaluation results
print(f"Test Accuracy: {accuracy * 100:.2f}%")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")
print("Confusion Matrix:")
print(conf_matrix)
print("Classification Report:")
print(report)
