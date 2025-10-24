import sqlite3
import json
from pathlib import Path

def export_to_json_with_sql(db_path: str, output_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Single SQL query that joins, groups, and orders links
    query = """
    SELECT
        json_object(
            'id', p.id,
            'first_name', p.first_name,
            'last_name', p.last_name,
            'email', p.email,
            'position', p.position,
            'description', p.description,
            'links', json_group_array(
                json_object(
                    'url', l.url,
                    'label', l.label
                )
            )
        ) AS person_json
    FROM people p
    LEFT JOIN (
        SELECT * FROM links ORDER BY label COLLATE NOCASE
    ) l ON p.id = l.person_id
    GROUP BY p.id;
    """

    cur.execute(query)
    rows = cur.fetchall()

    # Convert SQLite JSON results to Python objects
    people_json = [json.loads(row["person_json"]) for row in rows]

    # Write to a JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(people_json, f, indent=4, ensure_ascii=False)

    conn.close()
    print(f"✅ Exported {len(people_json)} people to {output_path} (includes position & description)")

if __name__ == "__main__":
    db_path = Path(__file__).parent / "database.db"
    output_path = Path(__file__).parent / "database.json"
    export_to_json_with_sql(db_path, output_path)
