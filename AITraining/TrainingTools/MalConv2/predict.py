import numpy as np
from tensorflow import keras
from malconv2 import MalConv2, read_file_bytes  

def predict_file(file_path):
    # Load model
    print(f"Loading model from ./models/malconv2_model.h5")
    model = keras.models.load_model("./models/malconv2_model.h5")
    print(f"Model loaded from ./models/malconv2_model.h5")
    
    # Read file bytes
    file_bytes = read_file_bytes(file_path, max_size=1000000)
    print(f"File bytes length: {len(file_bytes)}")  # Debug print for file size
    
    # Convert file bytes to a numerical format (e.g., uint8 array)
    file_data = np.frombuffer(file_bytes, dtype=np.uint8)
    print(f"File data shape after conversion: {file_data.shape}")
    
    # Reshape or expand the dimensions of file_data if necessary
    file_data = np.expand_dims(file_data, axis=0)  # Add batch dimension
    file_data = np.expand_dims(file_data, axis=-1)  # Add channel dimension if necessary
    print(f"File data shape after expansion: {file_data.shape}")
    
    # Make prediction
    prediction = model.predict(file_data)
    print(f"Prediction: {prediction}")  # Debug print for prediction output

    # Handle multi-class output
    if isinstance(prediction, np.ndarray):
        # If it's a multi-class prediction, get the index of the highest probability
        prediction_value = np.argmax(prediction, axis=1)[0]  # Select the index of the highest class
    else:
        prediction_value = prediction

    # Output result based on prediction class index
    if prediction_value == 0:
        print("The file is not a polyglot.")
    elif prediction_value == 1:
        print("The file is a polyglot.")
    else:
        print("Unknown prediction class.")

# Call the function with the file path
predict_file("/home/dmay/dillyDefender/AITraining/TrainingTools/D2/Detect.py")
