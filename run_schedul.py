import subprocess
import os
import time
import requests
import zipfile
from io import BytesIO
from requests.exceptions import Timeout, RequestException

# 🔧 CONFIGURATIONS
PS_SCRIPT_PATH = r"C:\Users\Administrator\Desktop\postgreSQL_backup\backup_postgres.ps1"
BACKUP_FOLDER = r"C:\Users\Administrator\Desktop\postgreSQL_backup\backups"  # Folder for backups
POSTGRES_BIN_PATH = r"C:\Program Files\PostgreSQL\13\bin"  # Update to your PostgreSQL bin path
DJANGO_API_URL = "http://185.221.237.182/Auth/upload-file/"  # Update with your API URL

# Supported backup file extensions (includes compressed backups)
BACKUP_EXTENSIONS = (".sql", ".backup", ".dump", ".tar", ".zip")

# Ensure PostgreSQL bin is in PATH
os.environ["PATH"] = POSTGRES_BIN_PATH + ";" + os.environ["PATH"]

# ✅ Step 1: Run PowerShell Script to Create Backup
def run_backup_script():
    """Runs the PowerShell backup script and checks if it executed successfully."""
    print("🚀 Running PowerShell backup script...")

    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", PS_SCRIPT_PATH], 
            check=True, capture_output=True, text=True
        )
        print("✅ PowerShell backup script executed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running PowerShell script: {e}")
        print(f"🔴 PowerShell Error Output:\n{e.stderr}")
        return False

    return True

# 🔍 Step 2: Find the Latest Backup File (Includes .zip)
def find_latest_backup():
    """Finds the most recent backup file (including compressed backups)."""
    latest_backup = None
    print(f"🔍 Checking backup folder: {BACKUP_FOLDER}")

    try:
        for file_name in os.listdir(BACKUP_FOLDER):
            file_path = os.path.join(BACKUP_FOLDER, file_name)
            print(f"📁 Found file: {file_name}")

            # Debugging: print the file extension matching check
            print(f"Extension Check: {file_name.lower().endswith(BACKUP_EXTENSIONS)}")

            if file_name.lower().endswith(BACKUP_EXTENSIONS) and os.path.isfile(file_path):
                print(f"✔️ File matches backup criteria: {file_name}")

                if latest_backup is None or os.path.getmtime(file_path) > os.path.getmtime(latest_backup):
                    latest_backup = file_path

        if latest_backup:
            print(f"✅ Latest backup found: {latest_backup}")
            return latest_backup
        else:
            print("❌ No backup file found.")
            return None
    except Exception as e:
        print(f"⚠️ Error finding backup: {e}")
        return None

# 📤 Step 3: Compress the Backup File
def compress_file(file_path):
    """Compresses the backup file only if it is not already a .zip file."""
    if file_path.endswith(".zip"):
        print(f"⚠️ File '{file_path}' is already a ZIP. Skipping compression.")
        return file_path  # Return the same file path, avoiding re-compression

    compressed_file_path = f"{file_path}.zip"
    try:
        print(f"📦 Compressing file: {file_path}")
        original_size = os.path.getsize(file_path)
        print(f"🔍 Original file size: {original_size} bytes")

        with zipfile.ZipFile(compressed_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_path, os.path.basename(file_path))
            print(f"✅ File compressed successfully into {compressed_file_path}")

        compressed_size = os.path.getsize(compressed_file_path)
        print(f"🔍 Compressed file size: {compressed_size} bytes")

    except Exception as e:
        print(f"❌ Error compressing file: {e}")
        return None

    return compressed_file_path  # Return the new compressed file path


# 📤 Step 4: Split Backup into Chunks
def split_file(file_path, chunk_size=10*1024*1024):
    """Splits the compressed backup file into smaller chunks."""
    chunks = []
    with open(file_path, 'rb') as f:
        chunk_number = 1
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break  # No more data to read
            chunk_file_name = f"{file_path}_part_{chunk_number}.zip"
            with open(chunk_file_name, 'wb') as chunk_file:
                chunk_file.write(chunk)
            chunks.append(chunk_file_name)
            print(f"Created chunk {chunk_number}: {chunk_file_name}")
            chunk_number += 1
    return chunks

# 📤 Step 5: Upload Chunked Backup to Django API (in Chunks)
def send_chunk_to_api(chunk_file_name):
    """Uploads a chunk of the backup file to the Django API."""
    try:
        with open(chunk_file_name, 'rb') as file:
            # Create a BytesIO object to hold the file's content in memory
            file_content = BytesIO(file.read())
            file_content.seek(0)  # Go to the start of the file content

            files = {'file': (os.path.basename(chunk_file_name), file_content)}

            # Retry logic in case of failure
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post(DJANGO_API_URL, files=files, timeout=600)  # 10 minutes timeout
                    if response.status_code == 200:
                        print(f"✅ Backup chunk '{chunk_file_name}' sent successfully!")
                        break
                    else:
                        print(f"❌ Failed to send chunk '{chunk_file_name}' to the API: {response.text}")
                        if attempt < max_retries - 1:
                            print(f"⏳ Retrying... (Attempt {attempt + 1}/{max_retries})")
                            time.sleep(5)
                except Timeout:
                    print(f"⚠️ Timeout error while sending chunk '{chunk_file_name}'. Retrying...")
                    if attempt < max_retries - 1:
                        time.sleep(5)
                except RequestException as e:
                    print(f"❌ Error with the request: {e}")
                    break
    except Exception as e:
        print(f"⚠️ Error sending chunk to API: {e}")

# 🔄 Step 6: Clean Up Files in Backup Directory
def clean_up_files():
    """Removes all files in the backup directory."""
    print("🧹 Cleaning up old files in backup directory...")
    try:
        for file_name in os.listdir(BACKUP_FOLDER):
            file_path = os.path.join(BACKUP_FOLDER, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"✅ Removed file: {file_name}")
    except Exception as e:
        print(f"❌ Error cleaning up files: {e}")

# ✅ Check ZIP Integrity
def check_zip_integrity(zip_file):
    """Checks the integrity of the zip file."""
    try:
        with zipfile.ZipFile(zip_file, 'r') as zipf:
            bad_file = zipf.testzip()
            if bad_file is not None:
                print(f"❌ Corrupted file in zip: {bad_file}")
            else:
                print(f"✅ Zip file '{zip_file}' is valid.")
    except zipfile.BadZipFile:
        print(f"❌ The file '{zip_file}' is not a valid ZIP file.")
    except Exception as e:
        print(f"⚠️ Error checking zip integrity: {e}")

# 🔄 Step 7: Automate the Backup Process Every 60 Minutes
def run_backup_cycle():
    """Runs the full backup cycle: create backup, find the latest, split it, and upload it."""
    while True:
        print("\n🔄 Starting new backup cycle...")

        # 1️⃣ Run PowerShell Script to Generate Backup
        if run_backup_script():
            time.sleep(5)  # Wait a few seconds to ensure file is saved

            # 2️⃣ Find Latest Backup File
            latest_backup = find_latest_backup()

            # 3️⃣ Compress the Backup File and Split into Chunks
            if latest_backup:
                compressed_backup = compress_file(latest_backup)
                if compressed_backup:
                    check_zip_integrity(compressed_backup)  # Check ZIP integrity

                    # 4️⃣ Split into Chunks if ZIP is Valid
                    chunks = split_file(compressed_backup)

                    # 5️⃣ Upload Each Chunk to API
                    for chunk in chunks:
                        send_chunk_to_api(chunk)

                # 5️⃣ Clean up files in backup folder
                clean_up_files()

        print("⏳ Waiting 15 minutes before next backup...")
        time.sleep(15 * 60)  # Wait for 15 minutes before the next backup

# 🚀 Start the Backup Process
if __name__ == "__main__":
    run_backup_cycle()
