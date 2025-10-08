import json
import mysql.connector
from datetime import datetime, date
import os

def default_converter(o):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    return str(o)

def backup_to_json(user="root", password="sina885", host="localhost", database="currency", backup_dir="backups_json"):
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = os.path.join(backup_dir, f"{database}_backup_{timestamp}.json")

    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SHOW TABLES;")
    tables = [t[f"Tables_in_{database}"] for t in cursor.fetchall()]

    data = {}
    for table in tables:
        cursor.execute(f"SELECT * FROM {table};")
        rows = cursor.fetchall()
        data[table] = rows

    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=default_converter)

    cursor.close()
    conn.close()

    print(f"✅ Backup saved as JSON: {backup_file}")


if __name__ == "__main__":
    backup_to_json()
