# Template Conversion Summary

This document explains the changes made to convert `minang-01.html` into a dynamic Jinja2 template (`templates/invitation.html`).

## Key Replacements Made

### 1. Meta Tags and Title
- **Title**: Changed from "Minang-01" to `{{ invitation.groom_nickname }} & {{ invitation.bride_nickname }}`
- **Meta description**: Now uses dynamic date formatting with Indonesian day/month names
- **OG tags**: Updated to use dynamic couple names and dates

### 2. Date Formatting
- Added `{% set date_info = invitation.event_date|indonesian_date %}` at the top of the template
- Replaced all hardcoded dates with dynamic variables:
  - Day name: `{{ date_info.day_name }}` (e.g., "Sabtu", "Minggu")
  - Day number: `{{ date_info.day }}`
  - Month name: `{{ date_info.month_name }}` (e.g., "Desember", "Januari")
  - Year: `{{ date_info.year }}`
  - Formatted date: `{{ date_info.formatted_date }}` (e.g., "13.04.2025")

### 3. Couple Names
- Replaced all instances of "Fulan & Fulannah" with:
  - `{{ invitation.groom_nickname }} & {{ invitation.bride_nickname }}`

### 4. Groom Information
- **Name**: `{{ invitation.groom_nickname }}`
- **Parents**: `{{ invitation.groom_parents }}` (replaces "Bapak Fulan dan Ibu Fulannah")
- **Instagram**: 
  - Link: `https://www.instagram.com/{{ invitation.groom_instagram|remove_at }}/`
  - Display: `{{ invitation.groom_instagram }}`
  - Conditionally displayed only if Instagram is provided
- **Photo**: `{{ invitation.groom_photo_url }}` (with fallback to default image)

### 5. Bride Information
- **Name**: `{{ invitation.bride_nickname }}`
- **Parents**: `{{ invitation.bride_parents }}` (replaces "Bapak Fulan dan Ibu Fulannah")
- **Instagram**: 
  - Link: `https://www.instagram.com/{{ invitation.bride_instagram|remove_at }}/`
  - Display: `{{ invitation.bride_instagram }}`
  - Conditionally displayed only if Instagram is provided
- **Photo**: `{{ invitation.bride_photo_url }}` (with fallback to default image)

### 6. Event Information

#### Akad Nikah Section
- **Date**: Uses `date_info` for day, month, year
- **Time**: `{{ invitation.akad_time }}` (replaces "10.00 - 11.00 WIB")
- **Location**: `{{ invitation.location_name }}` (replaces "Rumah Panggung Darusalam Palembang")

#### Resepsi Section
- **Date**: Uses `date_info` for day, month, year
- **Time**: `{{ invitation.resepsi_time }}` (replaces "19.00 WIB - Selesai")
- **Location**: `{{ invitation.location_name }}`

### 7. Location/Maps
- **Location name**: `{{ invitation.location_name }}` (multiple instances)
- **Google Maps embed**: `{{ invitation.location_map_link }}` (with fallback to default)
- **Google Maps link**: `{{ invitation.location_map_link }}` (with fallback to default)

### 8. Music/Audio
- **Audio source**: `{{ invitation.music_url }}` (with fallback to default music file)
- Applied to both `<audio>` tag and `<source>` tag

### 9. Bank Account Information
- **Account display**: `{{ invitation.bank_account }}` (with newline to `<br />` conversion)
- **Copy function**: Extracts account number from bank_account field for copy functionality
- Multiple instances in the "Kirim Hadiah" modal

### 10. Calendar Link
- **Google Calendar link**: Dynamically generated with:
  - Couple names (URL encoded)
  - Location name (URL encoded)
  - Event date in ISO format

### 11. JavaScript Variables
- Updated `ctnt` variable to use dynamic couple names:
  ```javascript
  var ctnt = "{{ invitation.groom_nickname }} & {{ invitation.bride_nickname }}";
  ```

## Custom Jinja2 Filters Added

### `indonesian_date` Filter
Converts a date object to Indonesian format with:
- Day name in Indonesian (Senin, Selasa, etc.)
- Month name in Indonesian (Januari, Februari, etc.)
- Formatted date string (DD.MM.YYYY)

### `remove_at` Filter
Removes the '@' symbol from Instagram usernames for URL construction.

## Conditional Rendering

Several elements are conditionally rendered:
- Instagram links only show if Instagram usernames are provided
- Photo URLs fall back to default images if not provided
- Music URL falls back to default if not provided
- Map links fall back to default if not provided

## Notes

- All external CSS/JS resources remain unchanged (loaded from CDN)
- All styling and animations are preserved
- The template maintains the exact same visual design
- Only data content is made dynamic

