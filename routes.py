import os
import json
import logging
from flask import render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from app import app, db
from models import CriminalRecord, DetectionResult
from face_detection import face_detection_service

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main dashboard page"""
    # Get recent detections
    recent_detections = DetectionResult.query.order_by(
        DetectionResult.detection_date.desc()
    ).limit(5).all()
    
    # Get statistics
    total_criminals = CriminalRecord.query.filter_by(is_active=True).count()
    total_detections = DetectionResult.query.count()
    matches_found = DetectionResult.query.filter_by(match_found=True).count()
    
    stats = {
        'total_criminals': total_criminals,
        'total_detections': total_detections,
        'matches_found': matches_found,
        'match_rate': round((matches_found / total_detections * 100) if total_detections > 0 else 0, 1)
    }
    
    return render_template('index.html', 
                         recent_detections=recent_detections,
                         stats=stats)

@app.route('/detect', methods=['POST'])
def detect_face():
    """Handle face detection from uploaded image"""
    try:
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('index'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload a PNG, JPG, or JPEG file.', 'error')
            return redirect(url_for('index'))
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Validate image
        is_valid, message = face_detection_service.validate_image(filepath)
        if not is_valid:
            os.remove(filepath)  # Clean up
            flash(message, 'error')
            return redirect(url_for('index'))
        
        # Extract face encoding from uploaded image
        face_encoding = face_detection_service.extract_face_encoding(filepath)
        
        if not face_encoding:
            os.remove(filepath)  # Clean up
            flash('No faces detected in the uploaded image', 'error')
            return redirect(url_for('index'))
        
        # Get all criminal records
        criminals = CriminalRecord.query.filter_by(is_active=True).all()
        
        if not criminals:
            # Create detection result with no match
            detection_result = DetectionResult(
                image_filename=filename,
                confidence_score=0.0,
                match_found=False
            )
            db.session.add(detection_result)
            db.session.commit()
            
            flash('No criminal records in database to compare against', 'warning')
            return redirect(url_for('results', detection_id=detection_result.id))
        
        # Compare against criminal database
        known_encodings = [criminal.face_encoding for criminal in criminals]
        matches = face_detection_service.compare_faces(known_encodings, face_encoding)
        
        # Create detection result
        if matches:
            # Get the best match
            best_match = matches[0]
            criminal = criminals[best_match['index']]
            
            detection_result = DetectionResult(
                image_filename=filename,
                criminal_id=criminal.id,
                confidence_score=best_match['confidence'],
                match_found=True
            )
            
            flash(f'Match found: {criminal.name} (Confidence: {best_match["confidence"]:.1f}%)', 'success')
        else:
            detection_result = DetectionResult(
                image_filename=filename,
                confidence_score=0.0,
                match_found=False
            )
            
            flash('No matches found in criminal database', 'info')
        
        db.session.add(detection_result)
        db.session.commit()
        
        return redirect(url_for('results', detection_id=detection_result.id))
        
    except Exception as e:
        logger.error(f"Error in face detection: {str(e)}")
        flash('An error occurred during face detection. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/results/<int:detection_id>')
def results(detection_id):
    """Display detection results"""
    detection = DetectionResult.query.get_or_404(detection_id)
    return render_template('results.html', detection=detection)

@app.route('/database')
def database():
    """Criminal database management page"""
    criminals = CriminalRecord.query.filter_by(is_active=True).order_by(
        CriminalRecord.date_added.desc()
    ).all()
    return render_template('database.html', criminals=criminals)

@app.route('/add_criminal', methods=['POST'])
def add_criminal():
    """Add new criminal record"""
    try:
        name = request.form.get('name', '').strip()
        alias = request.form.get('alias', '').strip()
        crime_type = request.form.get('crime_type', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name or not crime_type:
            flash('Name and crime type are required', 'error')
            return redirect(url_for('database'))
        
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('Photo is required for criminal record', 'error')
            return redirect(url_for('database'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('database'))
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload a PNG, JPG, or JPEG file.', 'error')
            return redirect(url_for('database'))
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Validate and extract face encoding
        is_valid, message = face_detection_service.validate_image(filepath)
        if not is_valid:
            os.remove(filepath)
            flash(message, 'error')
            return redirect(url_for('database'))
        
        face_encoding = face_detection_service.extract_face_encoding(filepath)
        
        if not face_encoding:
            os.remove(filepath)
            flash('No clear face detected in the uploaded photo. Please use a clear photo with a visible face.', 'error')
            return redirect(url_for('database'))
        
        # Create criminal record
        criminal = CriminalRecord(
            name=name,
            alias=alias if alias else None,
            crime_type=crime_type,
            description=description if description else None,
            face_encoding=json.dumps(face_encoding),
            image_filename=filename
        )
        
        db.session.add(criminal)
        db.session.commit()
        
        flash(f'Criminal record for {name} added successfully', 'success')
        return redirect(url_for('database'))
        
    except Exception as e:
        logger.error(f"Error adding criminal record: {str(e)}")
        flash('An error occurred while adding the criminal record. Please try again.', 'error')
        return redirect(url_for('database'))

@app.route('/delete_criminal/<int:criminal_id>', methods=['POST'])
def delete_criminal(criminal_id):
    """Delete criminal record"""
    try:
        criminal = CriminalRecord.query.get_or_404(criminal_id)
        
        # Soft delete - mark as inactive
        criminal.is_active = False
        db.session.commit()
        
        flash(f'Criminal record for {criminal.name} deleted successfully', 'success')
        return redirect(url_for('database'))
        
    except Exception as e:
        logger.error(f"Error deleting criminal record: {str(e)}")
        flash('An error occurred while deleting the criminal record. Please try again.', 'error')
        return redirect(url_for('database'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('500.html'), 500
