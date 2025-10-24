import sqlite3
from pathlib import Path

# --- CONFIG ---
DB_PATH = Path(__file__).parent / "database.db"

# --- CONNECT ---
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

def add_person():
    print("Add a New Person")

    fields = ["first_name", "last_name", "email", "position", "description"]
    new_data = {}

    for field in fields:
        if field == "description":
            print(f"Enter {field}: (Press Ctrl+D  when done)")
            lines = []
            while True:
                try:
                    line = input()
                except EOFError:
                    break
                lines.append(line)
            value = "\n".join(lines).strip()
        else:
            value = input(f"Enter {field}: ").strip()

        new_data[field] = value if value else None

    # Build SQL for person
    columns = ", ".join(new_data.keys())
    placeholders = ", ".join("?" for _ in new_data)
    sql = f"INSERT INTO people ({columns}) VALUES ({placeholders})"

    # Execute insertion
    cursor.execute(sql, list(new_data.values()))
    conn.commit()
    person_id = cursor.lastrowid

    print("\n✅ Added new person:")
    print(f"id: {person_id}")
    for field, value in new_data.items():
        print(f"{field}: {value}")

    # Add links
    add_links(person_id)

def add_links(person_id):
    print("\n🔗 Add Links (press Enter to skip)")
    while True:
        url = input("Enter link URL (or just Enter to finish): ").strip()
        if not url:
            break
        label = input("Enter link label (e.g. 'personal', 'GitHub', 'LinkedIn'): ").strip()

        cursor.execute(
            "INSERT INTO links (person_id, url, label) VALUES (?, ?, ?)",
            (person_id, url, label or None)
        )
        conn.commit()
        print(f"✅ Added link: {url} ({label})")

# --- MAIN ---
if __name__ == "__main__":
    try:
        add_person()
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()
