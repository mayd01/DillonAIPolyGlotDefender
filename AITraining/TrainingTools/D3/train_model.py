import numpy as np
import os
from sklearn.model_selection import train_test_split
from D22 import D22, create_model
from process_data import preprocess_and_save_data  # Import the preprocessing function

# Use memory mapping to load large numpy files efficiently
X_non_polyglots = np.load("/data/processed/X_non-polyglots.npy", mmap_mode='r')
X_polyglots = np.load("/data/processed/X_polyglots.npy", mmap_mode='r')
X_remaining = np.load("/data/processed/X_remaining.npy", mmap_mode='r')

y_non_polyglots = np.load("/data/processed/y_non-polyglots.npy", mmap_mode='r')
y_polyglots = np.load("/data/processed/y_polyglots.npy", mmap_mode='r')
y_remaining = np.load("/data/processed/y_remaining.npy", mmap_mode='r')

# Reshape X arrays to 2D arrays (n_samples, 1) if they are 1D
X_non_polyglots = X_non_polyglots.reshape(-1, 1)
X_polyglots = X_polyglots.reshape(-1, 1)
X_remaining = X_remaining.reshape(-1, 1)

# Debug prints for the shapes of each dataset
print("Shape of X_non_polyglots:", X_non_polyglots.shape)
print("Shape of X_polyglots:", X_polyglots.shape)
print("Shape of X_remaining:", X_remaining.shape)

# Combine all subsets
X = np.concatenate([X_non_polyglots, X_polyglots, X_remaining], axis=0)
y = np.concatenate([y_non_polyglots, y_polyglots, y_remaining], axis=0)

# Debug print for the shape of the combined dataset
print("Shape of X after concatenation:", X.shape)
print("Shape of y after concatenation:", y.shape)
print("Unique classes in y:", np.unique(y))

# Reshape X to 3D if it is 2D
if len(X.shape) == 2:
    X = X.reshape(X.shape[0], X.shape[1], 1)
    print("Reshaped X to 3D:", X.shape)
elif len(X.shape) == 3:
    print("X is already 3D, no reshape necessary.")
else:
    raise ValueError("X has an unexpected number of dimensions.")

print("Shape of X after reshape check:", X.shape)

try:
    # Performing a train-test split with 80-20 ratio
    print("Attempting manual train-test split...")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print("Shape of X_train:", X_train.shape)
    print("y_train sample:", y_train[:10])
    print("y_test sample:", y_test[:10])

    unique, counts = np.unique(y_train, return_counts=True)
    print("Training class distribution:", dict(zip(unique, counts)))

    print("Training set shape:", X_train.shape)
    print("Test set shape:", X_test.shape)
except Exception as e:
    print(f"Error during train-test split: {e}")

# Initialize and train the model
D22_model = D22()
try:
    print("Training D22 model...")
    D22_model.train(X_train, y_train, X_test, y_test, epochs=10, batch_size=32)
except Exception as e:
    print(f"Error during training: {e}")

# Save the model
try:
    D22_model.save("./models/D22_model.h5")
    print("Model saved successfully!")
except Exception as e:
    print(f"Error saving the model: {e}")
