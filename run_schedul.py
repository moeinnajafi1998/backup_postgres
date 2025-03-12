import subprocess
import os
import time

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

while True:
    get_backup()
    time.sleep(60*10)  # wait for ten minutes before checking again
