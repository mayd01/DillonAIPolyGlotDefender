import numpy as np
import os
from sklearn.model_selection import train_test_split
from malconv2 import MalConv2, create_model
from process_data import preprocess_and_save_data  # Import the preprocessing function

# Preprocess data and save it (This can be done separately before training)
# preprocess_and_save_data("/mnt/IronVault", "/mnt/IronVault/processed")

# Load preprocessed data (you only need to do this after preprocessing is complete)
X = np.load("/mnt/IronVault/processed/X.npy")
y = np.load("/mnt/IronVault/processed/y.npy")

# Reshape X for the model input (required for 1D convolutions)
X = X.reshape(X.shape[0], X.shape[1], 1)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the MalConv2 model
malconv2_model = MalConv2()  
malconv2_model.train(X_train, y_train, X_test, y_test, epochs=10, batch_size=32)

# Save the trained model
malconv2_model.save("./models/malconv2_model.h5")

# Evaluate the model on the test set
# loss, accuracy = malconv2_model.evaluate(X_test, y_test)
# print(f"Test loss: {loss}, Test accuracy: {accuracy}")
