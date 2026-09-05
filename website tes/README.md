# Wedding Invitation Generator

A Flask application that allows you to generate multiple dynamic wedding invitation links using a single HTML template.

## Features

- Create unlimited wedding invitations from a single template
- Dynamic URL structure: `domain.com/<slug>` (e.g., `/andri-sari`, `/john-doe`)
- Dashboard to manage all invitations
- No login required
- SQLite database for simplicity

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5000`

## Usage

1. **Create an Invitation**: Fill out the form on the dashboard with:
   - Groom and bride information (names, nicknames, parents, Instagram, photos)
   - Event details (date, times for Akad and Resepsi, location)
   - Additional information (music URL, bank account details)

2. **View Invitation**: Click the "View" button in the invitations list, or visit `http://localhost:5000/<slug>`

3. **Delete Invitation**: Click the "Delete" button next to any invitation in the list

## Database Model

The `Invitation` model includes:
- `slug`: Unique URL identifier
- Groom information: name, nickname, parents, Instagram, photo URL
- Bride information: name, nickname, parents, Instagram, photo URL
- Event information: date, akad time, resepsi time, location, map link
- Additional: music URL, bank account info

## Template Customization

The invitation template (`templates/invitation.html`) uses Jinja2 variables:
- `{{ invitation.groom_nickname }}` - Groom's nickname
- `{{ invitation.bride_nickname }}` - Bride's nickname
- `{{ invitation.event_date|indonesian_date }}` - Formatted event date
- And many more...

## Notes

- The application uses SQLite by default (database file: `invitations.db`)
- All static assets (CSS, JS, images) are loaded from external CDN sources
- Date formatting uses Indonesian month and day names
- The slug is automatically generated from groom and bride names

