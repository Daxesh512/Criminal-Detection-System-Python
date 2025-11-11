# Criminal Face Detection System

## Overview

This is a Flask-based web application for criminal face detection and recognition. The system allows users to upload images to detect faces and match them against a database of known criminal records. It uses computer vision technology to analyze facial features and provide identification results with confidence scores.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with configurable database backend (SQLite for development, PostgreSQL for production)
- **Web Server**: Gunicorn WSGI server for production deployment
- **Face Recognition**: Uses `face_recognition` library built on dlib for facial analysis

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default templating)
- **Styling**: Bootstrap 5 for responsive UI components
- **Icons**: Font Awesome for iconography
- **JavaScript**: Vanilla JavaScript for client-side interactions

### Data Storage
- **Primary Database**: SQLAlchemy with two main models:
  - `CriminalRecord`: Stores criminal information and face encodings
  - `DetectionResult`: Tracks detection attempts and results
- **File Storage**: Local filesystem for uploaded images in `uploads/` directory
- **Face Encodings**: Stored as JSON strings in the database

## Key Components

### Face Detection Service (`face_detection.py`)
- Extracts facial encodings from uploaded images
- Compares face encodings against known criminal database
- Configurable tolerance levels for matching accuracy

### Database Models (`models.py`)
- **CriminalRecord**: Contains personal information, crime details, and facial encodings
- **DetectionResult**: Logs all detection attempts with confidence scores and match status

### Web Routes (`routes.py`)
- Dashboard with statistics and recent detection results
- File upload and face detection processing
- Database management interface for criminal records

### Utilities (`utils/face_utils.py`)
- Image processing and face detection helper functions
- Face encoding generation and comparison utilities

## Data Flow

1. **Image Upload**: User uploads an image through the web interface
2. **Face Extraction**: System extracts face encodings from the uploaded image
3. **Database Comparison**: Compares extracted encodings against stored criminal records
4. **Results Generation**: Calculates confidence scores and determines matches
5. **Result Display**: Shows detection results with matched criminal information if found
6. **Logging**: Stores all detection attempts in the database for audit purposes

## External Dependencies

### Core Libraries
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and migrations
- **face_recognition**: Facial recognition and encoding
- **OpenCV**: Image processing capabilities
- **Pillow (PIL)**: Image manipulation and format conversion
- **Gunicorn**: WSGI HTTP server for production

### Frontend Dependencies (CDN)
- **Bootstrap 5**: UI framework and responsive design
- **Font Awesome**: Icon library
- **Google Fonts**: Typography (Inter font family)

### System Dependencies
- **PostgreSQL**: Production database (configured in .replit)
- **Various image libraries**: libjpeg, libpng, libtiff for image processing

## Deployment Strategy

### Development Environment
- Uses SQLite database for local development
- Flask development server with debug mode enabled
- Hot-reload capabilities for development

### Production Environment
- **Platform**: Configured for Replit autoscale deployment
- **Web Server**: Gunicorn with process management
- **Database**: PostgreSQL with connection pooling
- **Security**: ProxyFix middleware for proper header handling
- **File Uploads**: 16MB maximum file size limit
- **Port Configuration**: Runs on port 5000 with proper binding

### Configuration Management
- Environment variables for database URLs and secret keys
- Separate development and production configurations
- Secure session management with configurable secret keys

## Changelog
- June 16, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.