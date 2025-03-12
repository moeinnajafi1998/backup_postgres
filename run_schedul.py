import subprocess
import os
import time
import requests

# Path to your PowerShell script
ps_script_path = r"C:\Users\USER\Desktop\postgreSQL_backup\backup_postgres.ps1"
backup_folder = r"C:\Users\USER\Desktop\postgreSQL_backup\backups"  # Path to the backup folder

# Ensure the PostgreSQL bin folder is in the PATH environment variable
os.environ["PATH"] = r"C:\Program Files\PostgreSQL\17\bin;" + os.environ["PATH"]

def get_backup():
    # Remove the previous backup files
    for file_name in os.listdir(backup_folder):
        file_path = os.path.join(backup_folder, file_name)
        if os.path.isfile(file_path) and file_name.endswith(".sqlc"):  # Assuming the backup file ends with .backup
            try:
                os.remove(file_path)
                print(f"Deleted previous backup: {file_name}")
            except Exception as e:
                print(f"Failed to delete {file_name}: {e}")

    # Run the PowerShell script with the correct execution policy
    try:
        result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script_path], 
                                check=True, capture_output=True, text=True, cwd=backup_folder)
        print("PowerShell script executed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running PowerShell script: {e}")
        print("Error output:", e.stderr)

    # Find the latest .sqlc backup file
    latest_backup = None
    for file_name in os.listdir(backup_folder):
        if file_name.endswith(".sqlc"):
            file_path = os.path.join(backup_folder, file_name)
            if latest_backup is None or os.path.getmtime(file_path) > os.path.getmtime(latest_backup):
                latest_backup = file_path

    if latest_backup:
        print(f"Found latest backup: {latest_backup}")
        send_backup_to_telegram(latest_backup)
    else:
        print("No .sqlc backup found.")

# Telegram bot details
TELEGRAM_API_URL = "https://api.telegram.org/bot7624564348:AAGDgGcIJOP7sBG8m4eXJ1NuNJTtSNZajvg/sendDocument"
CHAT_ID = "121498617"

def send_backup_to_telegram(file_path):
    with open(file_path, 'rb') as file:
        response = requests.post(TELEGRAM_API_URL, data={'chat_id': CHAT_ID}, files={'document': file})
        if response.status_code == 200:
            print("Backup sent successfully to Telegram!")
        else:
            print(f"Failed to send backup to Telegram: {response.text}")

while True:
    get_backup()
    time.sleep(60 * 10)  # Wait for ten minutes before checking again
