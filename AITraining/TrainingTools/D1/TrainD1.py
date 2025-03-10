import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split

def extract_features(file_path, regions=[(0, 256), (-256, None)]):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        features = []
        for start, end in regions:
            features.append(data[start:end] if end else data[start:])
        return np.concatenate([np.frombuffer(f, dtype=np.uint8) for f in features])
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def load_dataset(polyglot_dir, non_polyglot_dir):
    X, y = [], []
    
    for label, folder in enumerate([non_polyglot_dir, polyglot_dir]):
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            features = extract_features(file_path)
            if features is not None:
                X.append(features)
                y.append(label)
    
    return np.array(X, dtype=object), np.array(y)

polyglot_dir = "path/to/polyglot_files"
non_polyglot_dir = "path/to/non-polyglot_files"

X, y = load_dataset(polyglot_dir, non_polyglot_dir)

max_length = max(len(x) for x in X)
X_padded = np.array([np.pad(x, (0, max_length - len(x)), mode='constant') for x in X])

X_train, X_test, y_train, y_test = train_test_split(X_padded, y, test_size=0.2, random_state=42)

model = keras.Sequential([
    keras.layers.Input(shape=(max_length,)),
    keras.layers.Dense(256, activation="relu"),
    keras.layers.Dense(128, activation="relu"),
    keras.layers.Dense(1, activation="sigmoid") 
])

model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy * 100:.2f}%")

model.save("polyglot_detector.h5")
