import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Masking, Conv1D, MaxPooling1D, BatchNormalization
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

def extract_byte_sequence(file_path, seq_length=4096):
    """Reads a file and converts it into a normalized byte sequence."""
    with open(file_path, 'rb') as f:
        data = f.read(seq_length)
    
    byte_sequence = np.frombuffer(data, dtype=np.uint8)

    scaler = MinMaxScaler(feature_range=(0, 1))
    normalized_sequence = scaler.fit_transform(byte_sequence.reshape(-1, 1)).flatten()
    
    if len(normalized_sequence) < seq_length:
        padded_seq = np.zeros(seq_length)
        padded_seq[:len(normalized_sequence)] = normalized_sequence
        return padded_seq
    else:
        return normalized_sequence[:seq_length]

# Directory where bad files are stored
bad_files_dir = "/mnt/shared/polyglots/"
bad_files = [os.path.join(bad_files_dir, f) for f in os.listdir(bad_files_dir)]

print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

# Extract byte sequences for each bad file
bad_sequences = np.array([extract_byte_sequence(f) for f in bad_files])

# Assuming that bad files are labeled as 0 (you can adjust if there's another label format)
bad_labels = np.zeros(len(bad_sequences))

# Reshape input data to (samples, timesteps, features)
X = bad_sequences.reshape((bad_sequences.shape[0], bad_sequences.shape[1], 1))

# Split the dataset into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, bad_labels, test_size=0.2, random_state=42)

# Define the model (CNN-LSTM hybrid architecture)
model = Sequential([
    Masking(mask_value=0.0, input_shape=(4096, 1)),
    Conv1D(64, 3, activation='relu'),  # Adding 1D CNN layer for feature extraction
    MaxPooling1D(2),  # MaxPooling layer
    BatchNormalization(),  # Adding BatchNormalization layer
    LSTM(128, return_sequences=True),
    Dropout(0.3),  # Increased dropout for better regularization
    LSTM(64),
    Dropout(0.3),
    Dense(64, activation='relu'),  # Increased dense layer size for better representation
    Dense(1, activation='sigmoid')  # Binary classification (good/bad file)
])

# Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Add early stopping and learning rate reduction on plateau
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=1e-6)

# Train the model
history = model.fit(X_train, y_train, epochs=30, batch_size=32, verbose=1, validation_data=(X_test, y_test),
                    callbacks=[early_stopping, reduce_lr])

# Evaluate the model on the test set
y_pred = model.predict(X_test)
y_pred_class = (y_pred > 0.5).astype(int)

# Print classification report (Precision, Recall, F1-Score)
print("Classification Report (Test Set):")
print(classification_report(y_test, y_pred_class))

# Evaluate the model on the training set (just to verify how well it performs on seen data)
y_train_pred = model.predict(X_train)
y_train_pred_class = (y_train_pred > 0.5).astype(int)

print("Classification Report (Training Set):")
print(classification_report(y_train, y_train_pred_class))

# Evaluate the model on all files in the bad_files_dir to see if all are classified as 'Bad'
bad_file_preds = model.predict(X)
bad_file_preds_class = (bad_file_preds > 0.5).astype(int)

# Print evaluation for all bad files
print("Evaluation on all files in the training directory:")
print(f"Number of Bad files classified as 'Good': {np.sum(bad_file_preds_class == 1)}")
print(f"Number of Bad files classified as 'Bad': {np.sum(bad_file_preds_class == 0)}")

# Save the trained model
model.save("bad_file_anomaly_detector_improved.h5")
print("Model saved successfully!")
