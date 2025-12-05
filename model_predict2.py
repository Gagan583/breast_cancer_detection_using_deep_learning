from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import cv2
import numpy as np
from matplotlib.pyplot import imread, imshow
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.imagenet_utils import decode_predictions, preprocess_input
from efficientnet.tfkeras import EfficientNetB0
from tensorflow.keras import models
from tensorflow.keras.layers import Dense, BatchNormalization, Dropout, Flatten
from tensorflow.keras.regularizers import l1
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import RMSprop
from efficientnet.tfkeras import EfficientNetB0
from tensorflow.keras import models
from tensorflow.keras.layers import Dense, BatchNormalization, Dropout, Flatten, GlobalAveragePooling2D
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.regularizers import l1
from tensorflow.keras.optimizers import RMSprop
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np
#Acne and Rosacea Photos


#Actinic Keratosis Basal Cell Carcinoma and other Malignant Lesions

#Atopic Dermatitis Photos

#Bullous Disease Photos
# Define your class names manually (in the same order as training)

# Define the class names
class_names = ["benign", "malignant"]

# Initialize and set the LabelEncoder with the class names
label_encoder = LabelEncoder()
label_encoder.classes_ = np.array(class_names)

# Number of classes based on the class names
num_classes = len(label_encoder.classes_)

# Load EfficientNetB0 without the top classification layers
efficientnet_model = EfficientNetB0(input_shape=(100,100, 3), include_top=False, weights='imagenet')

# Define the new model
inputs = efficientnet_model.input

# Get the output of the last convolutional layer for Grad-CAM
conv_output = efficientnet_model.layers[-1].output

# Add Global Average Pooling
x = GlobalAveragePooling2D()(conv_output)

# Add dense layers with regularization, batch normalization, and dropout
x = Dense(128, kernel_regularizer=l1(0.0001), activation='relu')(x)
x = BatchNormalization(renorm=True)(x)
x = Dropout(0.3)(x)

x = Dense(64, kernel_regularizer=l1(0.0001), activation='relu')(x)
x = BatchNormalization(renorm=True)(x)
x = Dropout(0.3)(x)

x = Dense(32, kernel_regularizer=l1(0.0001), activation='relu')(x)
x = BatchNormalization(renorm=True)(x)
x = Dropout(0.3)(x)

# Add the final classification layer
outputs = Dense(units=num_classes, activation='softmax')(x)

# Combine into the model
model = models.Model(inputs=inputs, outputs=outputs)

# Compile the model
custom_optimizer = RMSprop(learning_rate=0.0001)
model.compile(optimizer=custom_optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Load the saved weights
model.load_weights('breakhis efficent_model.h5')

print("Model loaded successfully!")



# Preprocess the image
def preprocess_single_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Error loading image: {image_path}")
    
    # Resize the image to target size
    image = cv2.resize(image, (100,100))
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_enhanced = clahe.apply(gray)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(clahe_enhanced, (5, 5), 0)
    
    # Apply Canny edge detection
    edges = cv2.Canny(blurred, threshold1=50, threshold2=150)
    
    # Create an RGB edge map (edges in red)
    edges_colored = np.zeros_like(image)
    edges_colored[:, :, 2] = edges
    
    # Overlay the edges onto the original image
    processed_image = cv2.addWeighted(image, 0.8, edges_colored, 0.5, 0)

    cv2.imwrite("static/output_image.png",processed_image)
    
    # Normalize the image (scaling pixel values between 0 and 1)
    processed_image = processed_image / 255.0
    
    return np.expand_dims(processed_image, axis=0)





'''def pred_skin_disease(img_path):
# Path to the image
            image_path =img_path
            preprocessed_image = preprocess_single_image(image_path)

            # Make prediction
            predictions = model.predict(preprocessed_image)

            # Decode the predicted label
            predicted_label = label_encoder.inverse_transform([np.argmax(predictions)])
            confidence = np.max(predictions)

            print(f"Predicted Label: {predicted_label[0]}, Confidence: {confidence * 100:.2f}%")

            return predicted_label[0]
'''
import tensorflow as tf
import matplotlib.cm as cm

# ==============================
# Grad-CAM Function
# ==============================
def make_gradcam_heatmap(img_array, model, last_conv_layer_name, pred_index=None):
    # Create a model that maps the input image to the activations of the last conv layer
    # and the final predictions
    grad_model = tf.keras.models.Model(
        [model.inputs], 
        [model.get_layer(last_conv_layer_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        if pred_index is None:
            pred_index = tf.argmax(predictions[0])
        class_channel = predictions[:, pred_index]

    # Get gradients of the predicted class with respect to the last conv layer
    grads = tape.gradient(class_channel, conv_outputs)

    # Compute guided gradients (mean intensity of the gradients across channels)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    # Normalize heatmap between 0 & 1 for visualization
    heatmap = tf.maximum(heatmap, 0) / tf.reduce_max(heatmap)
    return heatmap.numpy()


def save_and_display_gradcam(img_path, heatmap, cam_path="static/grad_result.png", alpha=0.4):
    # Load original image
    img = cv2.imread(img_path)
    img = cv2.resize(img, (100,100))

    # Rescale heatmap to 0-255
    heatmap = np.uint8(255 * heatmap)

    # Apply the heatmap using jet colormap
    jet = cm.get_cmap("jet")
    jet_colors = jet(np.arange(256))[:, :3]
    jet_heatmap = jet_colors[heatmap]

    jet_heatmap = cv2.resize(jet_heatmap, (img.shape[1], img.shape[0]))
    jet_heatmap = np.uint8(255 * jet_heatmap)

    # Superimpose heatmap on original image
    superimposed_img = cv2.addWeighted(img, 1 - alpha, jet_heatmap, alpha, 0)

    # Save the Grad-CAM result
    cv2.imwrite(cam_path, superimposed_img)
    print(f"Grad-CAM saved at: {cam_path}")
    return cam_path


# ==============================
# Update prediction function
# ==============================
def pred_skin_disease(img_path):
    preprocessed_image = preprocess_single_image(img_path)

    # Make prediction
    predictions = model.predict(preprocessed_image)
    predicted_class = np.argmax(predictions)
    predicted_label = label_encoder.inverse_transform([predicted_class])
    confidence = np.max(predictions)

    print(f"Predicted Label: {predicted_label[0]}, Confidence: {confidence * 100:.2f}%")

    # Generate Grad-CAM
    last_conv_layer_name = "top_conv"   # For EfficientNetB0 last conv layer
    heatmap = make_gradcam_heatmap(preprocessed_image, model, last_conv_layer_name, pred_index=predicted_class)

    # Save Grad-CAM result
    save_and_display_gradcam(img_path, heatmap, cam_path="static/grad_result.png")

    return predicted_label[0],confidence

#pred_sugar_cane("benign-familial-chronic-pemphigus-10.jpg")