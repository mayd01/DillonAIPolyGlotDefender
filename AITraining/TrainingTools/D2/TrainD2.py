import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split

# Function to extract specific byte regions from files
def extract_features(file_path, regions=[(0, 256), (-256, None)]):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        
        if len(data) < 256:  # Handle small files
            print(f"Skipping {file_path}: File too small")
            return None
        
        features = [data[start:end] if end is not None else data[start:] for start, end in regions]
        return np.concatenate([np.frombuffer(f, dtype=np.uint8) / 255.0 for f in features])
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# Load dataset
# Load dataset
def load_dataset(polyglot_dir, non_polyglot_dir):
    X, y = [], []
    
    for label, folder in enumerate([non_polyglot_dir, polyglot_dir]):
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            print(f"Processing {file_path}...")
            features = extract_features(file_path)
            print(f"Features: {features}")
            if features is not None:
                X.append(features)
                y.append(label)
    
    # Ensure X is a numpy array with consistent data type
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32)  # np.int32 if it's a classification problem

# Paths to datasets (Update these paths)
polyglot_dir = "/mnt/shared/polyglots"
non_polyglot_dir = "/mnt/shared/non-polyglots"

# Load data
print("Loading dataset...")
X, y = load_dataset(polyglot_dir, non_polyglot_dir)
print("Dataset loaded.")
# Convert to consistent shape (padding/truncation)
print("Padding sequences...")
max_length = max(len(x) for x in X)
X_padded = np.array([np.pad(x, (0, max_length - len(x)), mode='constant') for x in X], dtype=np.float32)
print("Sequences padded.")
# Reshape data for CNN input (samples, sequence_length, channels)
X_padded = X_padded.reshape(X_padded.shape[0], max_length, 1)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_padded, y, test_size=0.2, random_state=42)

# Define CNN model
model = keras.Sequential([
    keras.layers.Conv1D(filters=64, kernel_size=5, activation="relu", input_shape=(max_length, 1)),
    keras.layers.MaxPooling1D(pool_size=2),
    keras.layers.Conv1D(filters=128, kernel_size=5, activation="relu"),
    keras.layers.MaxPooling1D(pool_size=2),
    keras.layers.Conv1D(filters=256, kernel_size=5, activation="relu"),
    keras.layers.Flatten(),  # Instead of GlobalAveragePooling1D
    keras.layers.Dense(128, activation="relu"),
    keras.layers.Dropout(0.3),  # Prevent overfitting
    keras.layers.Dense(1, activation="sigmoid")
])

print("Model summary:")
# Compile model
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
print(model.summary())
# Save best model checkpoint
checkpoint = keras.callbacks.ModelCheckpoint(
    "polyglot_cnn_detector_best.h5", save_best_only=True, monitor="val_accuracy", mode="max"
)

print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
print("Training model...")
# Train model
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test), callbacks=[checkpoint])
print("Training complete.")

# Evaluate model
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy * 100:.2f}%")

model.save("polyglot_cnn_detector_final.h5")
