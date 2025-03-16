import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import layers, models
from tensorflow.keras import regularizers

def create_model(input_shape=(1000000,)):
    model = models.Sequential([
        layers.InputLayer(input_shape=input_shape),
        layers.Reshape((input_shape[0], 1)), 
        
        # Convolutional layers with more filters
        layers.Conv1D(64, 5, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        
        layers.Conv1D(128, 5, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        
        layers.Conv1D(256, 5, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        
        layers.GlobalMaxPooling1D(),  # or Flatten
        
        # Fully connected layers
        layers.Dense(512, activation='relu', kernel_regularizer=regularizers.l2(0.01)),
        layers.Dropout(0.5),  # Dropout to prevent overfitting
        layers.Dense(3, activation='softmax')  # Change to multi-class for polyglot/virus types
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
