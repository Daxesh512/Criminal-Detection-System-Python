import cv2
import numpy as np
import json
import logging
from PIL import Image
import os
import hashlib

logger = logging.getLogger(__name__)

class FaceDetectionService:
    """Service for face detection using OpenCV"""
    
    def __init__(self):
        self.tolerance = 0.6  # Face matching tolerance
        # Load OpenCV's pre-trained face detection model
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def extract_face_encoding(self, image_path):
        """Extract a simple face 'encoding' from an image using basic features"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                logger.warning(f"Could not load image: {image_path}")
                return None
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                logger.warning(f"No faces found in image: {image_path}")
                return None
            
            # Get the largest face (most prominent)
            largest_face = max(faces, key=lambda face: face[2] * face[3])
            x, y, w, h = largest_face
            
            # Extract face region
            face_region = gray[y:y+h, x:x+w]
            
            # Resize to standard size for comparison
            face_resized = cv2.resize(face_region, (100, 100))
            
            # Create a simple feature vector using histogram and basic statistics
            # This is a simplified approach compared to deep learning encodings
            hist = cv2.calcHist([face_resized], [0], None, [256], [0, 256])
            
            # Normalize histogram
            hist = hist.flatten()
            hist = hist / (hist.sum() + 1e-7)
            
            # Add some basic statistical features
            mean_val = np.mean(face_resized)
            std_val = np.std(face_resized)
            
            # Combine features into a simple encoding
            encoding = np.concatenate([hist, [mean_val, std_val]])
            
            return encoding.tolist()
            
        except Exception as e:
            logger.error(f"Error extracting face encoding from {image_path}: {str(e)}")
            return None
    
    def compare_faces(self, known_encodings, face_encoding):
        """Compare a face encoding against known criminal encodings using cosine similarity"""
        try:
            if not known_encodings or not face_encoding:
                return []
            
            # Convert known encodings from JSON strings to numpy arrays
            known_face_encodings = []
            for i, encoding_str in enumerate(known_encodings):
                try:
                    encoding = json.loads(encoding_str)
                    known_face_encodings.append((i, np.array(encoding)))
                except json.JSONDecodeError:
                    logger.error("Invalid face encoding format in database")
                    continue
            
            if not known_face_encodings:
                return []
            
            # Convert face encoding to numpy array
            face_encoding_array = np.array(face_encoding)
            
            # Calculate similarities
            results = []
            for i, (orig_index, known_encoding) in enumerate(known_face_encodings):
                # Calculate cosine similarity
                dot_product = np.dot(face_encoding_array, known_encoding)
                norm_a = np.linalg.norm(face_encoding_array)
                norm_b = np.linalg.norm(known_encoding)
                
                if norm_a == 0 or norm_b == 0:
                    similarity = 0
                else:
                    similarity = dot_product / (norm_a * norm_b)
                
                # Convert similarity to confidence percentage
                confidence = max(0, similarity * 100)
                
                # Consider it a match if confidence is above threshold
                if confidence > (self.tolerance * 100):
                    results.append({
                        'index': orig_index,
                        'confidence': confidence,
                        'distance': 1 - similarity
                    })
            
            # Sort by confidence (highest first)
            results.sort(key=lambda x: x['confidence'], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error comparing faces: {str(e)}")
            return []
    
    def detect_faces_in_image(self, image_path):
        """Detect all faces in an image and return their locations"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return []
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Convert to format similar to face_recognition library
            face_locations = []
            for (x, y, w, h) in faces:
                # Convert from (x, y, w, h) to (top, right, bottom, left)
                face_locations.append((y, x+w, y+h, x))
            
            return face_locations
            
        except Exception as e:
            logger.error(f"Error detecting faces in {image_path}: {str(e)}")
            return []
    
    def validate_image(self, image_path):
        """Validate if image is suitable for face detection"""
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                return False, "Image file not found"
            
            # Try to open with PIL
            with Image.open(image_path) as img:
                # Check image format
                if img.format not in ['JPEG', 'PNG', 'JPG']:
                    return False, "Unsupported image format. Please use JPEG or PNG."
                
                # Check image size
                width, height = img.size
                if width < 100 or height < 100:
                    return False, "Image too small. Please use an image at least 100x100 pixels."
                
                if width > 4000 or height > 4000:
                    return False, "Image too large. Please use an image smaller than 4000x4000 pixels."
            
            # Try to load with OpenCV to ensure compatibility
            test_image = cv2.imread(image_path)
            if test_image is None:
                return False, "Could not load image with OpenCV"
            
            return True, "Valid image"
            
        except Exception as e:
            logger.error(f"Error validating image {image_path}: {str(e)}")
            return False, f"Invalid image file: {str(e)}"

# Global instance
face_detection_service = FaceDetectionService()
