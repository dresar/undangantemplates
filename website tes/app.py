from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory
from models import db, Invitation
from datetime import datetime
import os
import re
import calendar
import locale
import json
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invitations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'media/photos'
app.config['AUDIO_FOLDER'] = 'media/audio'
app.config['GALLERY_FOLDER'] = 'media/gallery'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['ALLOWED_AUDIO_EXTENSIONS'] = {'mp3', 'wav', 'ogg', 'm4a'}

db.init_app(app)

# Create upload folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)
os.makedirs(app.config['GALLERY_FOLDER'], exist_ok=True)

# Indonesian month and day names
INDONESIAN_MONTHS = {
    1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
    5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
    9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
}

INDONESIAN_DAYS = {
    0: 'Minggu', 1: 'Senin', 2: 'Selasa', 3: 'Rabu',
    4: 'Kamis', 5: 'Jumat', 6: 'Sabtu'
}

@app.template_filter('indonesian_date')
def indonesian_date_filter(date):
    """Format date in Indonesian format"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    day_name = INDONESIAN_DAYS[date.weekday()]
    month_name = INDONESIAN_MONTHS[date.month]
    return {
        'day_name': day_name,
        'day': date.day,
        'month_name': month_name,
        'month': date.month,
        'year': date.year,
        'formatted_date': f"{date.day:02d}.{date.month:02d}.{date.year}"
    }

@app.template_filter('remove_at')
def remove_at_filter(text):
    """Remove @ symbol from Instagram username"""
    if text:
        return text.replace('@', '')
    return ''

@app.template_filter('from_json')
def from_json_filter(text):
    """Parse JSON string to Python object"""
    if text:
        try:
            return json.loads(text)
        except:
            return []
    return []

def create_slug(name):
    """Generate a URL-friendly slug from a name"""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = re.sub(r'^-+|-+$', '', slug)
    return slug

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def allowed_audio_file(filename):
    """Check if audio file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_AUDIO_EXTENSIONS']

def save_uploaded_file(file, prefix, folder='photos'):
    """Save uploaded file and return filename only"""
    if not file or not file.filename:
        return None
    
    # Determine folder and allowed extensions
    if folder == 'audio':
        if not allowed_audio_file(file.filename):
            return None
        upload_folder = app.config['AUDIO_FOLDER']
    elif folder == 'gallery':
        if not allowed_file(file.filename):
            return None
        upload_folder = app.config['GALLERY_FOLDER']
    else:  # photos
        if not allowed_file(file.filename):
            return None
        upload_folder = app.config['UPLOAD_FOLDER']
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    unique_filename = f"{prefix}_{timestamp}_{name}{ext}"
    filepath = os.path.join(upload_folder, unique_filename)
    file.save(filepath)
    return unique_filename

@app.route('/')
def dashboard():
    invitations = Invitation.query.order_by(Invitation.created_at.desc()).all()
    return render_template('dashboard.html', invitations=invitations)

@app.route('/create', methods=['POST'])
def create_invitation():
    try:
        # Generate slug from groom and bride names
        groom_name = request.form.get('groom_name', '').strip()
        bride_name = request.form.get('bride_name', '').strip()
        base_slug = f"{groom_name}-{bride_name}".lower()
        slug = create_slug(base_slug)
        
        # Ensure slug is unique
        counter = 1
        original_slug = slug
        while Invitation.query.filter_by(slug=slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        # Parse event date
        event_date_str = request.form.get('event_date')
        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        except:
            flash('Format tanggal tidak valid. Gunakan format YYYY-MM-DD.', 'error')
            return redirect(url_for('dashboard'))
        
        # Handle file uploads
        groom_photo_filename = None
        bride_photo_filename = None
        
        if 'groom_photo' in request.files:
            groom_file = request.files['groom_photo']
            if groom_file.filename:
                groom_photo_filename = save_uploaded_file(groom_file, 'groom')
                if not groom_photo_filename:
                    flash('Format file foto pria tidak didukung. Gunakan JPG, PNG, atau GIF.', 'error')
                    return redirect(url_for('dashboard'))
        
        if 'bride_photo' in request.files:
            bride_file = request.files['bride_photo']
            if bride_file.filename:
                bride_photo_filename = save_uploaded_file(bride_file, 'bride')
                if not bride_photo_filename:
                    flash('Format file foto wanita tidak didukung. Gunakan JPG, PNG, atau GIF.', 'error')
                    return redirect(url_for('dashboard'))
        
        # Store filename in database (will be used to construct URL)
        groom_photo_url = groom_photo_filename if groom_photo_filename else ''
        bride_photo_url = bride_photo_filename if bride_photo_filename else ''
        
        # Handle audio upload
        music_filename = None
        if 'music_file' in request.files:
            music_file = request.files['music_file']
            if music_file.filename:
                music_filename = save_uploaded_file(music_file, 'music', 'audio')
                if not music_filename:
                    flash('Format file audio tidak didukung. Gunakan MP3, WAV, atau OGG.', 'error')
                    return redirect(url_for('dashboard'))
        
        # Handle gallery photos (multiple files)
        gallery_filenames = []
        if 'gallery_photos' in request.files:
            gallery_files = request.files.getlist('gallery_photos')
            for idx, gallery_file in enumerate(gallery_files):
                if gallery_file.filename:
                    gallery_filename = save_uploaded_file(gallery_file, f'gallery_{idx}', 'gallery')
                    if gallery_filename:
                        gallery_filenames.append(gallery_filename)
        
        # Handle story moments (JSON)
        import json
        story_moments = []
        story_count = int(request.form.get('story_count', 0))
        for i in range(story_count):
            year = request.form.get(f'story_{i}_year', '').strip()
            title = request.form.get(f'story_{i}_title', '').strip()
            text = request.form.get(f'story_{i}_text', '').strip()
            
            # Handle story photo upload
            story_photo_filename = None
            if f'story_{i}_photo' in request.files:
                story_file = request.files[f'story_{i}_photo']
                if story_file.filename:
                    story_photo_filename = save_uploaded_file(story_file, f'story_{i}', 'gallery')
            
            if year or title or text or story_photo_filename:
                story_moments.append({
                    'year': year,
                    'title': title,
                    'text': text,
                    'photo': story_photo_filename or ''
                })
        
        invitation = Invitation(
            slug=slug,
            groom_name=request.form.get('groom_name', '').strip(),
            groom_nickname=request.form.get('groom_nickname', '').strip(),
            groom_parents=request.form.get('groom_parents', '').strip(),
            groom_instagram=request.form.get('groom_instagram', '').strip(),
            groom_photo_url=groom_photo_url or '',
            bride_name=request.form.get('bride_name', '').strip(),
            bride_nickname=request.form.get('bride_nickname', '').strip(),
            bride_parents=request.form.get('bride_parents', '').strip(),
            bride_instagram=request.form.get('bride_instagram', '').strip(),
            bride_photo_url=bride_photo_url or '',
            event_date=event_date,
            akad_time=request.form.get('akad_time', '').strip(),
            resepsi_time=request.form.get('resepsi_time', '').strip(),
            location_name=request.form.get('location_name', '').strip(),
            location_map_link=request.form.get('location_map_link', '').strip(),
            music_url=music_filename or '',
            bank_account=request.form.get('bank_account', '').strip(),
            story_moments=json.dumps(story_moments) if story_moments else None,
            gallery_photos=json.dumps(gallery_filenames) if gallery_filenames else None,
            video_url=request.form.get('video_url', '').strip()
        )
        
        db.session.add(invitation)
        db.session.commit()
        flash(f'Undangan berhasil dibuat! Lihat di /{slug}', 'success')
    except RequestEntityTooLarge:
        flash('File terlalu besar. Maksimal 5MB per file.', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error saat membuat undangan: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/<slug>')
def view_invitation(slug):
    invitation = Invitation.query.filter_by(slug=slug).first_or_404()
    return render_template('invitation.html', invitation=invitation)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_invitation(id):
    invitation = Invitation.query.get_or_404(id)
    slug = invitation.slug
    
    # Delete associated photo files
    if invitation.groom_photo_url:
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], invitation.groom_photo_url)
        if os.path.exists(photo_path):
            try:
                os.remove(photo_path)
            except:
                pass
    
    if invitation.bride_photo_url:
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], invitation.bride_photo_url)
        if os.path.exists(photo_path):
            try:
                os.remove(photo_path)
            except:
                pass
    
    # Delete audio file
    if invitation.music_url:
        audio_path = os.path.join(app.config['AUDIO_FOLDER'], invitation.music_url)
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass
    
    # Delete gallery photos
    if invitation.gallery_photos:
        try:
            photos = json.loads(invitation.gallery_photos)
            for photo in photos:
                photo_path = os.path.join(app.config['GALLERY_FOLDER'], photo)
                if os.path.exists(photo_path):
                    try:
                        os.remove(photo_path)
                    except:
                        pass
        except:
            pass
    
    # Delete story photos
    if invitation.story_moments:
        try:
            moments = json.loads(invitation.story_moments)
            for moment in moments:
                if moment.get('photo'):
                    photo_path = os.path.join(app.config['GALLERY_FOLDER'], moment['photo'])
                    if os.path.exists(photo_path):
                        try:
                            os.remove(photo_path)
                        except:
                            pass
        except:
            pass
    
    db.session.delete(invitation)
    db.session.commit()
    flash(f'Undangan "{slug}" berhasil dihapus.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/media/photos/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded photos"""
    # Extract just the filename if full path is provided
    if '/' in filename:
        filename = filename.split('/')[-1]
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/media/audio/<path:filename>')
def uploaded_audio(filename):
    """Serve uploaded audio files"""
    if '/' in filename:
        filename = filename.split('/')[-1]
    return send_from_directory(app.config['AUDIO_FOLDER'], filename)

@app.route('/media/gallery/<path:filename>')
def uploaded_gallery(filename):
    """Serve uploaded gallery photos"""
    if '/' in filename:
        filename = filename.split('/')[-1]
    return send_from_directory(app.config['GALLERY_FOLDER'], filename)

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Try to add missing columns if they don't exist (for existing databases)
        try:
            from sqlalchemy import text, inspect
            inspector = inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('invitations')]
            
            with db.engine.connect() as conn:
                # Add story_moments column if it doesn't exist
                if 'story_moments' not in existing_columns:
                    conn.execute(text("ALTER TABLE invitations ADD COLUMN story_moments TEXT"))
                    conn.commit()
                    print("Added column 'story_moments'")
                
                # Add gallery_photos column if it doesn't exist
                if 'gallery_photos' not in existing_columns:
                    conn.execute(text("ALTER TABLE invitations ADD COLUMN gallery_photos TEXT"))
                    conn.commit()
                    print("Added column 'gallery_photos'")
                
                # Add video_url column if it doesn't exist
                if 'video_url' not in existing_columns:
                    conn.execute(text("ALTER TABLE invitations ADD COLUMN video_url VARCHAR(500)"))
                    conn.commit()
                    print("Added column 'video_url'")
        except Exception as e:
            print(f"Note: Could not auto-migrate database: {e}")
            print("If you see column errors, delete invitations.db and restart the app")
    
    app.run(debug=True)

