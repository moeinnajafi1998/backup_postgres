$DB_NAME = "postgres"
$DB_USER = "postgres"
$DB_HOST = "localhost"
$BACKUP_DIR = "C:\Users\USER\Desktop\postgreSQL_backup\backups"
$TIMESTAMP = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$BACKUP_FILE = "$BACKUP_DIR\backup_$TIMESTAMP.sqlc"

# Ensure the backup directory exists
if (!(Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null
}

# Run pg_dump
$env:PGPASSWORD = "M123m321m"
pg_dump -U $DB_USER -h $DB_HOST -F c -f $BACKUP_FILE $DB_NAME

# Optional: Delete old backups (keep last 24 backups)
$OldBackups = Get-ChildItem -Path $BACKUP_DIR -Filter "backup_*.sqlc" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 24
$OldBackups | Remove-Item -Force
