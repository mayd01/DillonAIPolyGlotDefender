import tensorflow as tf

# List all available GPUs
gpus = tf.config.list_physical_devices('GPU')

if gpus:
    print(f"✅ GPU detected: {gpus}")
else:
    print("❌ No GPU detected, running on CPU.")
