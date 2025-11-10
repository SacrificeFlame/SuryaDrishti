#!/usr/bin/env python3
"""
Database backup script for SuryaDrishti
Supports PostgreSQL backup to local filesystem or S3
"""
import os
import sys
import subprocess
import datetime
import boto3
from pathlib import Path
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backup_postgresql_to_file(backup_path: str) -> bool:
    """Backup PostgreSQL database using pg_dump"""
    try:
        from urllib.parse import urlparse
        db_url = settings.database_url_processed
        parsed = urlparse(db_url)
        
        # Extract connection details
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        database = parsed.path.lstrip("/")
        user = parsed.username
        password = parsed.password
        
        # Build pg_dump command
        env = os.environ.copy()
        if password:
            env["PGPASSWORD"] = password
        
        cmd = [
            "pg_dump",
            "-h", host,
            "-p", str(port),
            "-U", user or "postgres",
            "-d", database,
            "-F", "c",  # Custom format
            "-f", backup_path,
            "-v"  # Verbose
        ]
        
        logger.info(f"Running pg_dump to {backup_path}")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Backup completed successfully: {backup_path}")
            return True
        else:
            logger.error(f"Backup failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error during backup: {e}", exc_info=True)
        return False

def backup_sqlite_to_file(backup_path: str) -> bool:
    """Backup SQLite database by copying the file"""
    try:
        db_url = settings.DATABASE_URL
        # Extract database file path from sqlite:///path/to/db
        db_path = db_url.replace("sqlite:///", "")
        
        if not os.path.exists(db_path):
            logger.error(f"Database file not found: {db_path}")
            return False
        
        import shutil
        shutil.copy2(db_path, backup_path)
        logger.info(f"SQLite backup completed: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error during SQLite backup: {e}", exc_info=True)
        return False

def upload_to_s3(backup_path: str, s3_key: str) -> bool:
    """Upload backup file to S3"""
    try:
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            logger.warning("AWS credentials not configured, skipping S3 upload")
            return False
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.BACKUP_S3_REGION or 'us-east-1'
        )
        
        s3_client.upload_file(
            backup_path,
            settings.BACKUP_S3_BUCKET,
            s3_key
        )
        
        logger.info(f"Uploaded backup to S3: s3://{settings.BACKUP_S3_BUCKET}/{s3_key}")
        return True
        
    except Exception as e:
        logger.error(f"Error uploading to S3: {e}", exc_info=True)
        return False

def cleanup_old_backups(backup_dir: str, retention_days: int):
    """Remove backup files older than retention_days"""
    try:
        backup_path = Path(backup_dir)
        if not backup_path.exists():
            return
        
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
        
        for backup_file in backup_path.glob("*.dump") or backup_path.glob("*.db"):
            file_time = datetime.datetime.fromtimestamp(backup_file.stat().st_mtime)
            if file_time < cutoff_date:
                backup_file.unlink()
                logger.info(f"Removed old backup: {backup_file}")
                
    except Exception as e:
        logger.error(f"Error cleaning up old backups: {e}", exc_info=True)

def main():
    """Main backup function"""
    if not settings.BACKUP_ENABLED:
        logger.info("Backups are disabled in configuration")
        return
    
    # Create backup directory
    backup_dir = Path(settings.BACKUP_STORAGE_PATH)
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if settings.DATABASE_URL.startswith("sqlite"):
        backup_filename = f"suryadrishti_backup_{timestamp}.db"
    else:
        backup_filename = f"suryadrishti_backup_{timestamp}.dump"
    
    backup_path = backup_dir / backup_filename
    
    # Perform backup
    if settings.DATABASE_URL.startswith("sqlite"):
        success = backup_sqlite_to_file(str(backup_path))
    else:
        success = backup_postgresql_to_file(str(backup_path))
    
    if not success:
        logger.error("Backup failed")
        sys.exit(1)
    
    # Upload to S3 if configured
    if settings.BACKUP_S3_BUCKET:
        s3_key = f"backups/{backup_filename}"
        upload_to_s3(str(backup_path), s3_key)
    
    # Cleanup old backups
    cleanup_old_backups(str(backup_dir), settings.BACKUP_RETENTION_DAYS)
    
    logger.info("Backup process completed successfully")

if __name__ == "__main__":
    main()

