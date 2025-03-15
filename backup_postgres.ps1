# Define PostgreSQL variables
$PG_USER = "postgres"
$PG_PASSWORD = "HamedMobina1234"
$PG_HOST = "localhost"
$PG_PORT = "5432"
$BACKUP_DIR = "C:\Users\Administrator\Desktop\postgreSQL_backup\backups"
$DATE = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$BACKUP_FILE = "$BACKUP_DIR\sina2025_backup_$DATE.sql"
$DB_NAME = "sina2025"

# Ensure backup directory exists
if (!(Test-Path -Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null
}

# Set PostgreSQL binary path
$PG_BIN = "C:\Program Files\PostgreSQL\13\bin"
$env:Path += ";$PG_BIN"

# Export password for authentication
$env:PGPASSWORD = $PG_PASSWORD

# Run backup command for the specific database
Write-Output "Backing up database $DB_NAME to $BACKUP_FILE..."
& "$PG_BIN\pg_dump.exe" -h $PG_HOST -p $PG_PORT -U $PG_USER -d $DB_NAME -f $BACKUP_FILE

# Check if the backup file was created
if (Test-Path $BACKUP_FILE) {
    # Compress the backup
    Compress-Archive -Path $BACKUP_FILE -DestinationPath "$BACKUP_FILE.zip"

    # Delete the uncompressed SQL file
    Remove-Item -Path $BACKUP_FILE -Force
    Write-Output "Backup completed: $BACKUP_FILE.zip"
} else {
    Write-Output "Backup failed: No backup file created."
}

# Unset the password environment variable
Remove-Item Env:PGPASSWORD
