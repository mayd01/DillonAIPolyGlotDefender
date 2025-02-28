import os
import numpy as np
import magic
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler

# Function to extract byte frequency features from a file
def extract_features(file_path):
    with open(file_path, "rb") as f:
        file_data = f.read()

    # Byte frequency distribution (256 possible byte values)
    byte_freq = np.zeros(256, dtype=int)
    for byte in file_data:
        byte_freq[byte] += 1

    # Normalize the byte frequencies
    byte_freq = byte_freq / len(file_data)
    
    # Additional feature: File type detection using python-magic
    file_type = magic.Magic(mime=True).from_file(file_path)
    file_type = file_type.split('/')[0]  # Extract top-level type (e.g., 'image', 'text', etc.)

    # Add the file type as an additional feature (one-hot encoded)
    types = ['image', 'text', 'application', 'audio', 'video', 'pdf', 'zip', 'executable']
    type_features = np.zeros(len(types), dtype=int)
    if file_type in types:
        type_features[types.index(file_type)] = 1

    # Concatenate byte frequencies with type features
    return np.concatenate((byte_freq, type_features))

# Function to load files and their labels
def load_dataset(polyglot_dir, non_polyglot_dir):
    X = []
    y = []

    # Load polyglot files (labeled as 1)
    for file_name in os.listdir(polyglot_dir):
        file_path = os.path.join(polyglot_dir, file_name)
        if os.path.isfile(file_path):
            X.append(extract_features(file_path))
            y.append(1)

    # Load non-polyglot files (labeled as 0)
    for file_name in os.listdir(non_polyglot_dir):
        file_path = os.path.join(non_polyglot_dir, file_name)
        if os.path.isfile(file_path):
            X.append(extract_features(file_path))
            y.append(0)

    return np.array(X), np.array(y)

# Paths to your datasets (modify with actual paths)
polyglot_dir = 'path/to/polyglot_files'  # Directory containing polyglot files
non_polyglot_dir = 'path/to/non_polyglot_files'  # Directory containing non-polyglot files

# Load dataset
X, y = load_dataset(polyglot_dir, non_polyglot_dir)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the data for better Random Forest performance (optional but helps)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Initialize and train the Random Forest classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")

# Save the trained model and scaler for later use
import joblib
joblib.dump(model, 'polyglot_rf_model.pkl')
joblib.dump(scaler, 'scaler.pkl')

# Optionally, you can also save the feature names for reference
feature_names = ['byte_freq_' + str(i) for i in range(256)] + \
                ['file_type_' + str(i) for i in range(len(['image', 'text', 'application', 'audio', 'video', 'pdf', 'zip', 'executable']))]
with open('feature_names.txt', 'w') as f:
    for name in feature_names:
        f.write(f"{name}\n")
