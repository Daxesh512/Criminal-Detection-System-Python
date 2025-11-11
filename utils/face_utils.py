import cv2
import face_recognition
import numpy as np
from PIL import Image
import logging

def load_image(image_path):
    """Load image from file path"""
    try:
        # Load image using PIL first to handle various formats
        pil_image = Image.open(image_path)
        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        # Convert to numpy array for face_recognition
        image = np.array(pil_image)
        return image
    except Exception as e:
        logging.error(f"Error loading image {image_path}: {str(e)}")
        return None

def detect_faces(image):
    """Detect faces in an image and return face locations"""
    try:
        # Use face_recognition to detect faces
        face_locations = face_recognition.face_locations(image, model='hog')
        return face_locations
    except Exception as e:
        logging.error(f"Error detecting faces: {str(e)}")
        return []

def get_face_encoding(image, face_location):
    """Get face encoding for a specific face location"""
    try:
        # Get face encoding
        face_encodings = face_recognition.face_encodings(image, [face_location])
        if face_encodings:
            return face_encodings[0]
        return None
    except Exception as e:
        logging.error(f"Error getting face encoding: {str(e)}")
        return None

def compare_faces(known_encodings, face_encoding, tolerance=0.6):
    """Compare a face encoding against known encodings"""
    try:
        # Use face_recognition's face_distance for more precise comparison
        distances = face_recognition.face_distance(known_encodings, face_encoding)
        return distances
    except Exception as e:
        logging.error(f"Error comparing faces: {str(e)}")
        return [1.0]  # Return max distance on error

def calculate_confidence(distance):
    """Calculate confidence percentage from face distance"""
    if distance > 1.0:
        return 0.0
    return (1.0 - distance) * 100

def is_match(distance, threshold=0.6):
    """Determine if a face is a match based on distance threshold"""
    return distance < threshold
