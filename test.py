import tensorflow as tf

# Check if TensorFlow can detect GPUs
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
