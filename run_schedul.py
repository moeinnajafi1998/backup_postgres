import subprocess
import os
import time
import requests

# Path to your PowerShell script
ps_script_path = r"C:\Users\Administrator\Desktop\postgreSQL_backup\backup_postgres.ps1"
backup_folder = r"C:\Users\Administrator\Desktop\postgreSQL_backup\backups"  # Path to the backup folder

# Ensure the PostgreSQL bin folder is in the PATH environment variable
os.environ["PATH"] = r"C:\Program Files\PostgreSQL\13\bin;" + os.environ["PATH"]

# Django API details
DJANGO_API_URL = "http://185.221.237.182/Auth/upload-file/"  # Change this to your actual Django API URL

def get_backup():
    # Remove the previous backup files
    for file_name in os.listdir(backup_folder):
        file_path = os.path.join(backup_folder, file_name)
        if os.path.isfile(file_path) and file_name.endswith(".sqlc"):  # Assuming the backup file ends with .sqlc
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
    print(f"Checking backup folder: {backup_folder}")
    for file_name in os.listdir(backup_folder):
        file_path = os.path.join(backup_folder, file_name)
        print(f"Found file: {file_name}")
        if file_name.endswith(".sqlc"):  # Check if the file ends with .sqlc
            if latest_backup is None or os.path.getmtime(file_path) > os.path.getmtime(latest_backup):
                latest_backup = file_path

    if latest_backup:
        print(f"Found latest backup: {latest_backup}")
        send_backup_to_api(latest_backup)
    else:
        print("No .sqlc backup found.")
        
def send_backup_to_api(file_path):
    """Send the backup file to the Django API with 'iran_server' appended to the filename."""
    try:
        if os.path.getsize(file_path) == 0:
            print(f"The backup file {file_path} is empty. Skipping upload.")
            return
        
        # Extract file name and extension
        base_name, extension = os.path.splitext(os.path.basename(file_path))
        
        # Append "iran_server" to the file name
        new_file_name = f"{base_name}_iran_server{extension}"
        
        with open(file_path, 'rb') as file:
            files = {'file': (new_file_name, file)}  # Set new file name when uploading
            response = requests.post(DJANGO_API_URL, files=files)
            
            if response.status_code == 200:
                print(f"Backup '{new_file_name}' sent successfully to the API!")
            else:
                print(f"Failed to send backup '{new_file_name}' to the API: {response.text}")
    except Exception as e:
        print(f"Error sending backup to API: {e}")


while True:
    get_backup()
    time.sleep(10 * 60)  # Wait for ten minutes before checking again
