import numpy as np
from tensorflow import keras
from malconv2 import MalConv2, read_file_bytes  

def predict_file(file_path):
    # Load model
    model = keras.models.load_model("./models/malconv2_model.h5")

    file_bytes = read_file_bytes(file_path, max_size=1000000)
    file_data = np.expand_dims(file_bytes, axis=0)

    prediction = model.predict(file_data)

    if prediction >= 0.5:
        print("The file is a polyglot.")
    else:
        print("The file is not a polyglot.")

    predict_file("./mnt/IronVault/new_file_to_predict.exe")
