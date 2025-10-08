import os
from datetime import datetime

def backup_mysql(user="root", password="sina885", database="currency", backup_dir="backups"):
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = os.path.join(backup_dir, f"{database}_backup_{timestamp}.sql")

    command = f"mysqldump -u {user} -p{password} {database} > {backup_file}"
    os.system(command)

    print(f" Backup saved at {backup_file}")

if __name__ == "__main__":
    backup_mysql()
