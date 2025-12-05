import cv2
import numpy as np
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import load_model
from tensorflow.keras.applications import MobileNet
from tensorflow.keras import models
from tensorflow.keras.layers import Dense, BatchNormalization, Dropout, GlobalAveragePooling2D
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.regularizers import l1
from tensorflow.keras.optimizers import RMSprop

# Updated class names
class_names = ["cancor", "unknown"]

# Label encoding
label_encoder = LabelEncoder()
label_encoder.classes_ = np.array(class_names)
num_classes = len(label_encoder.classes_)

# Load MobileNet base model
mobilenet_model = MobileNet(input_shape=(100, 100, 3), include_top=False, weights='imagenet')

# Custom classifier head
inputs = mobilenet_model.input
conv_output = mobilenet_model.layers[-1].output

x = GlobalAveragePooling2D()(conv_output)
x = Dense(128, kernel_regularizer=l1(0.0001), activation='relu')(x)
x = BatchNormalization(renorm=True)(x)
x = Dropout(0.3)(x)

x = Dense(64, kernel_regularizer=l1(0.0001), activation='relu')(x)
x = BatchNormalization(renorm=True)(x)
x = Dropout(0.3)(x)

x = Dense(32, kernel_regularizer=l1(0.0001), activation='relu')(x)
x = BatchNormalization(renorm=True)(x)
x = Dropout(0.3)(x)

outputs = Dense(units=num_classes, activation='softmax')(x)

# Create and compile the model
model = models.Model(inputs=inputs, outputs=outputs)
custom_optimizer = RMSprop(learning_rate=0.0001)
model.compile(optimizer=custom_optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Load trained weights
model.load_weights("mobilenet_unknown_class.h5")
print("MobileNet model with 4 disease classes loaded successfully!")

# Preprocess image from frame (not from path)
def preprocess_frame(frame):
    if frame is None:
        raise ValueError("Empty frame received from camera")
    
    frame = cv2.resize(frame, (100, 100))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_enhanced = clahe.apply(gray)
    
    blurred = cv2.GaussianBlur(clahe_enhanced, (5, 5), 0)
    edges = cv2.Canny(blurred, threshold1=50, threshold2=150)
    
    edges_colored = np.zeros_like(frame)
    edges_colored[:, :, 2] = edges
    
    processed_frame = cv2.addWeighted(frame, 0.8, edges_colored, 0.5, 0)
    
    # (Optional) Save processed frame for debugging
    cv2.imwrite("static/output_frame.png", processed_frame)
    
    processed_frame = processed_frame / 255.0
    return np.expand_dims(processed_frame, axis=0)
from PIL import Image
# Prediction using frame
def pred_unknown(image_path):
    # Open image file
    img = Image.open(image_path)
    # Convert to numpy array
    frame = np.array(img)
    # Preprocess as before
    preprocessed_image = preprocess_frame(frame)
    predictions = model.predict(preprocessed_image)
    predicted_label = label_encoder.inverse_transform([np.argmax(predictions)])
    confidence = np.max(predictions)
    
    print("Prediction array:", predictions)
    print(f"Predicted Class: {predicted_label[0]}, Confidence: {confidence * 100:.2f}%")
    return predicted_label[0], predictions


# Example usage
#pred_disease_class("/kaggle/working/dataset_livliness/no_live/12_frame6.png")
#pred_disease_class("download (10).jpg")
