import numpy as np
from tensorflow import keras
from tensorflow.keras import layers

def create_model(input_shape=(1000000,)):
    """Create and return the MalConv2 model."""
    model = keras.Sequential([
        layers.InputLayer(input_shape=input_shape),
        layers.Reshape((input_shape[0], 1)), 
        layers.Conv1D(64, 3, padding='same', activation='relu'),
        layers.Conv1D(128, 3, padding='same', activation='relu'),
        layers.Conv1D(256, 3, padding='same', activation='relu'),
        layers.GlobalMaxPooling1D(),
        layers.Dense(256, activation='relu'),
        layers.Dense(2, activation='softmax')  
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

class MalConv2:
    def __init__(self, model=None):
        """Initialize the MalConv2 model."""
        if model is None:
            self.model = create_model()
        else:
            self.model = model

    def train(self, X_train, y_train, X_test, y_test, epochs=10, batch_size=32):
        """Train the model."""
        self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_test, y_test))

    def save(self, path):
        """Save the trained model to the given path."""
        self.model.save(path)

    def evaluate(self, X_test, y_test):
        """Evaluate the model on the test data."""
        return self.model.evaluate(X_test, y_test)
