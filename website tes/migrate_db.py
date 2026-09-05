"""
Migration script to add new columns to existing database
Run this once to update your database schema: python migrate_db.py
"""
from app import app, db
from sqlalchemy import text, inspect

with app.app_context():
    try:
        # Get existing columns
        inspector = inspect(db.engine)
        existing_columns = [col['name'] for col in inspector.get_columns('invitations')]
        
        with db.engine.connect() as conn:
            # Add story_moments column if it doesn't exist
            if 'story_moments' not in existing_columns:
                conn.execute(text("ALTER TABLE invitations ADD COLUMN story_moments TEXT"))
                conn.commit()
                print("✓ Added column 'story_moments'")
            else:
                print("✓ Column 'story_moments' already exists")
            
            # Add gallery_photos column if it doesn't exist
            if 'gallery_photos' not in existing_columns:
                conn.execute(text("ALTER TABLE invitations ADD COLUMN gallery_photos TEXT"))
                conn.commit()
                print("✓ Added column 'gallery_photos'")
            else:
                print("✓ Column 'gallery_photos' already exists")
            
            # Add video_url column if it doesn't exist
            if 'video_url' not in existing_columns:
                conn.execute(text("ALTER TABLE invitations ADD COLUMN video_url VARCHAR(500)"))
                conn.commit()
                print("✓ Added column 'video_url'")
            else:
                print("✓ Column 'video_url' already exists")
        
        print("\n✅ Migration completed successfully!")
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        print("\nIf migration fails, you can:")
        print("1. Delete invitations.db and restart the app (will recreate database)")
        print("2. Or manually run SQL: ALTER TABLE invitations ADD COLUMN ...")

