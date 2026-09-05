from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Invitation(db.Model):
    __tablename__ = 'invitations'
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    
    # Groom information
    groom_name = db.Column(db.String(200), nullable=False)
    groom_nickname = db.Column(db.String(100), nullable=False)
    groom_parents = db.Column(db.String(300), nullable=False)
    groom_instagram = db.Column(db.String(100))
    groom_photo_url = db.Column(db.String(500))
    
    # Bride information
    bride_name = db.Column(db.String(200), nullable=False)
    bride_nickname = db.Column(db.String(100), nullable=False)
    bride_parents = db.Column(db.String(300), nullable=False)
    bride_instagram = db.Column(db.String(100))
    bride_photo_url = db.Column(db.String(500))
    
    # Event information
    event_date = db.Column(db.Date, nullable=False)
    akad_time = db.Column(db.String(50), nullable=False)
    resepsi_time = db.Column(db.String(50), nullable=False)
    location_name = db.Column(db.String(300), nullable=False)
    location_map_link = db.Column(db.String(500))
    
    # Additional information
    music_url = db.Column(db.String(500))  # filename for uploaded audio
    bank_account = db.Column(db.String(500))
    
    # Story/Timeline (JSON string to store multiple story moments)
    story_moments = db.Column(db.Text)  # JSON: [{"year": "2018", "title": "PERKENALAN", "photo": "filename.jpg", "text": "..."}, ...]
    
    # Gallery photos (JSON string to store multiple photo filenames)
    gallery_photos = db.Column(db.Text)  # JSON: ["photo1.jpg", "photo2.jpg", ...]
    
    # Video pre-wedding
    video_url = db.Column(db.String(500))  # YouTube URL or video embed URL
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Invitation {self.slug}>'

