import sqlite3
import sys
import re
from pathlib import Path

# --- CONFIG ---
BACKEND_DB = Path(__file__).parent / "database.db"
PERSONAL_DB = str(Path.home() / "life/database/database.db")

def categorize_url(url, description=""):
    """
    Categorize URLs based on the URL content and description.
    Similar logic to add.py
    """
    url_lower = url.lower()
    desc_lower = description.lower() if description else ""
    
    # Check URL patterns
    if "instagram.com" in url_lower or "instagram" in desc_lower:
        return "Instagram"
    elif "linkedin.com" in url_lower or "linkedin" in desc_lower:
        return "LinkedIn"
    elif "facebook.com" in url_lower or "facebook" in desc_lower:
        return "Facebook"
    elif "twitter.com" in url_lower or "x.com" in url_lower or "twitter" in desc_lower:
        return "Twitter"
    elif "github.com" in url_lower or "github" in desc_lower:
        return "GitHub"
    elif "youtube.com" in url_lower or "youtu.be" in url_lower or "youtube" in desc_lower:
        return "YouTube"
    else:
        return "Website"

def extract_urls_from_description(description):
    """
    Extract URLs from description text.
    Returns list of URLs found.
    """
    if not description:
        return []
    
    # Regex pattern to find URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, description)
    return urls

def copy_person(person_id):
    """
    Copy a person and their associated data from personal database to backend database.
    """
    # Connect to both databases
    personal_conn = sqlite3.connect(PERSONAL_DB)
    personal_conn.row_factory = sqlite3.Row
    personal_cursor = personal_conn.cursor()
    
    backend_conn = sqlite3.connect(BACKEND_DB)
    backend_cursor = backend_conn.cursor()
    
    try:
        # Fetch person data from personal database
        personal_cursor.execute(
            "SELECT * FROM people WHERE id = ?", 
            (person_id,)
        )
        person = personal_cursor.fetchone()
        
        if not person:
            print(f"❌ Error: Person with id {person_id} not found in personal database")
            return
        
        print(f"\n📋 Found person: {person['firstName']} {person['lastName']}")
        
        # Map fields from personal DB to backend DB
        # Personal DB: firstName, lastName, email, phoneNumber, priority, description
        # Backend DB: first_name, last_name, email, position, description, reader
        
        first_name = person['firstName'] or ""
        last_name = person['lastName'] or ""
        email = person['email'] or f"{first_name.lower()}.{last_name.lower()}@example.com"
        description = ""
        
        # Ask for job title/position
        position = input("Enter position/job title (or press Enter to skip): ").strip()
        position = position if position else None
        
        # Ask if they are a You vs You reader
        reader_input = input("Is this person a 'You vs You' reader? (y/n): ").strip().lower()
        reader = 1 if reader_input == 'y' else 0
        
        # Check if person already exists in backend database
        backend_cursor.execute(
            "SELECT id FROM people WHERE email = ?",
            (email,)
        )
        existing = backend_cursor.fetchone()
        
        if existing:
            print(f"⚠️  Warning: Person with email {email} already exists in backend database")
            response = input("Do you want to update this person? (y/n): ").strip().lower()
            if response != 'y':
                print("❌ Aborted")
                return
            new_person_id = existing[0]
            
            # Update existing person
            backend_cursor.execute(
                """UPDATE people 
                   SET first_name = ?, last_name = ?, position = ?, description = ?, reader = ?
                   WHERE id = ?""",
                (first_name, last_name, position, description, reader, new_person_id)
            )
            print(f"✅ Updated person with id {new_person_id}")
        else:
            # Insert new person
            backend_cursor.execute(
                """INSERT INTO people (first_name, last_name, email, position, description, reader)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (first_name, last_name, email, position, description, reader)
            )
            backend_conn.commit()
            new_person_id = backend_cursor.lastrowid
            print(f"✅ Added person with new id {new_person_id}")
        
        # Extract URLs from description
        urls_from_description = extract_urls_from_description(description)
        
        # Fetch website data from personal database
        personal_cursor.execute(
            "SELECT * FROM websites WHERE person_id = ?",
            (person_id,)
        )
        website = personal_cursor.fetchone()
        
        # Collect all URLs and their labels
        links_to_add = []
        
        # Add website URL if exists
        if website and website['url']:
            url = website['url']
            label = categorize_url(url, website['description'] or "")
            links_to_add.append((url, label))
        
        # Add URLs extracted from description
        for url in urls_from_description:
            label = categorize_url(url, description)
            links_to_add.append((url, label))
        
        # Insert links into backend database
        if links_to_add:
            print(f"\n🔗 Adding {len(links_to_add)} link(s):")
            for url, label in links_to_add:
                # Check if link already exists
                backend_cursor.execute(
                    "SELECT id FROM links WHERE person_id = ? AND url = ?",
                    (new_person_id, url)
                )
                if backend_cursor.fetchone():
                    print(f"  ⚠️  Link already exists: {url} ({label})")
                    continue
                
                backend_cursor.execute(
                    "INSERT INTO links (person_id, url, label) VALUES (?, ?, ?)",
                    (new_person_id, url, label)
                )
                print(f"  ✅ Added link: {url} ({label})")
        else:
            print("\n📭 No links to add")
        
        backend_conn.commit()
        
        print(f"\n✅ Successfully copied person {person_id} to backend database as person {new_person_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        backend_conn.rollback()
        raise
    finally:
        personal_conn.close()
        backend_conn.close()

# --- MAIN ---
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_from_personal_database.py <person_id>")
        sys.exit(1)
    
    try:
        person_id = int(sys.argv[1])
        copy_person(person_id)
    except ValueError:
        print("❌ Error: person_id must be an integer")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
