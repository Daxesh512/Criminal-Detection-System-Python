from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float

class CriminalRecord(db.Model):
    """Model for storing criminal records with face encodings"""
    __tablename__ = 'criminal_records'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    alias = Column(String(100))
    crime_type = Column(String(100), nullable=False)
    description = Column(Text)
    face_encoding = Column(Text, nullable=False)  # JSON string of face encoding
    image_filename = Column(String(255))
    date_added = Column(DateTime, default=datetime.utcnow)
    is_active = Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<CriminalRecord {self.name}>'

class DetectionResult(db.Model):
    """Model for storing face detection results"""
    __tablename__ = 'detection_results'
    
    id = Column(Integer, primary_key=True)
    image_filename = Column(String(255), nullable=False)
    criminal_id = Column(Integer, db.ForeignKey('criminal_records.id'))
    confidence_score = Column(Float, nullable=False)
    detection_date = Column(DateTime, default=datetime.utcnow)
    match_found = Column(db.Boolean, default=False)
    
    # Relationship
    criminal = db.relationship('CriminalRecord', backref='detections')
    
    def __repr__(self):
        return f'<DetectionResult {self.image_filename} - {self.confidence_score}>'
