#!/usr/bin/env python
"""
Script to migrate data from SQLite to PostgreSQL database.

This script:
1. Exports all data from SQLite database using Django's dumpdata command
2. Creates a PostgreSQL database configuration
3. Imports the data into PostgreSQL using Django's loaddata command

Usage:
    python migrate_sqlite_to_postgres.py

Prerequisites:
    - PostgreSQL server must be installed and running
    - Configure your PostgreSQL credentials in .env file
    - Set USE_POSTGRES=False initially to dump from SQLite
    - Backup your SQLite database before running this script
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(message):
    """Print a formatted header message."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(message):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message):
    """Print an error message."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_warning(message):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def print_info(message):
    """Print an info message."""
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")


def run_command(command, error_message="Command failed"):
    """Run a shell command and handle errors."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"{error_message}")
        print_error(f"Error: {e.stderr}")
        return None


def check_prerequisites():
    """Check if all prerequisites are met."""
    print_header("Checking Prerequisites")
    
    # Check if SQLite database exists
    if not Path('db.sqlite3').exists():
        print_error("SQLite database (db.sqlite3) not found!")
        return False
    print_success("SQLite database found")
    
    # Check if .env file exists
    if not Path('.env').exists():
        print_warning(".env file not found. Make sure to configure PostgreSQL credentials.")
        response = input("Do you want to continue? (y/n): ")
        if response.lower() != 'y':
            return False
    else:
        print_success(".env file found")
    
    # Check if PostgreSQL is installed
    result = subprocess.run(
        "psql --version",
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print_success(f"PostgreSQL installed: {result.stdout.strip()}")
    else:
        print_warning("PostgreSQL client (psql) not found in PATH")
        print_info("Make sure PostgreSQL is installed and accessible")
    
    return True


def backup_sqlite():
    """Create a backup of the SQLite database."""
    print_header("Backing Up SQLite Database")
    
    backup_name = f"db.sqlite3.backup_{subprocess.check_output(['date', '+%Y%m%d_%H%M%S']).decode().strip()}"
    
    try:
        import shutil
        shutil.copy2('db.sqlite3', backup_name)
        print_success(f"Backup created: {backup_name}")
        return True
    except Exception as e:
        print_error(f"Failed to create backup: {e}")
        return False


def dump_sqlite_data():
    """Dump data from SQLite database."""
    print_header("Dumping Data from SQLite")
    
    # Set environment to use SQLite
    env = os.environ.copy()
    env['USE_POSTGRES'] = 'False'
    
    print_info("Exporting data from SQLite database...")
    
    # Dump all data except contenttypes and auth.Permission (these will be auto-created)
    result = subprocess.run(
        "python manage.py dumpdata "
        "--natural-foreign --natural-primary "
        "--exclude contenttypes --exclude auth.Permission "
        "--indent 2 > data_dump.json",
        shell=True,
        env=env,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # Check if dump file has data
        if Path('data_dump.json').exists():
            with open('data_dump.json', 'r') as f:
                data = json.load(f)
                print_success(f"Data exported successfully! ({len(data)} objects)")
                return True
        else:
            print_error("Dump file was not created")
            return False
    else:
        print_error("Failed to dump data from SQLite")
        print_error(f"Error: {result.stderr}")
        return False


def setup_postgresql_db():
    """Setup PostgreSQL database."""
    print_header("Setting Up PostgreSQL Database")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    db_name = os.getenv('DB_NAME', 'topgrade_db')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    
    print_info(f"Database: {db_name}")
    print_info(f"User: {db_user}")
    print_info(f"Host: {db_host}:{db_port}")
    
    print_warning("\nMake sure PostgreSQL server is running!")
    print_info("You may need to create the database manually using:")
    print_info(f"  CREATE DATABASE {db_name};")
    print_info(f"  CREATE USER {db_user} WITH PASSWORD '{db_password}';")
    print_info(f"  GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};")
    
    response = input("\nHave you created the PostgreSQL database? (y/n): ")
    if response.lower() != 'y':
        print_warning("Please create the database first and run this script again.")
        return False
    
    return True


def migrate_postgresql():
    """Run migrations on PostgreSQL database."""
    print_header("Running Migrations on PostgreSQL")
    
    # Set environment to use PostgreSQL
    env = os.environ.copy()
    env['USE_POSTGRES'] = 'True'
    
    print_info("Running Django migrations on PostgreSQL...")
    
    result = subprocess.run(
        "python manage.py migrate --noinput",
        shell=True,
        env=env,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print_success("Migrations completed successfully!")
        print(result.stdout)
        return True
    else:
        print_error("Migration failed!")
        print_error(f"Error: {result.stderr}")
        return False


def load_data_to_postgresql():
    """Load dumped data into PostgreSQL."""
    print_header("Loading Data into PostgreSQL")
    
    if not Path('data_dump.json').exists():
        print_error("data_dump.json not found!")
        return False
    
    # Set environment to use PostgreSQL
    env = os.environ.copy()
    env['USE_POSTGRES'] = 'True'
    
    print_info("Importing data into PostgreSQL database...")
    
    result = subprocess.run(
        "python manage.py loaddata data_dump.json",
        shell=True,
        env=env,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print_success("Data imported successfully!")
        print(result.stdout)
        return True
    else:
        print_error("Failed to load data into PostgreSQL")
        print_error(f"Error: {result.stderr}")
        return False


def verify_data():
    """Verify data in PostgreSQL database."""
    print_header("Verifying Data Migration")
    
    # Set environment to use PostgreSQL
    env = os.environ.copy()
    env['USE_POSTGRES'] = 'True'
    
    # Count records in some key tables
    tables = ['auth.User', 'topgrade_api.CustomUser']
    
    for table in tables:
        app_label, model = table.split('.')
        result = subprocess.run(
            f"python manage.py shell -c \"from django.apps import apps; "
            f"model = apps.get_model('{app_label}', '{model}'); "
            f"print(model.objects.count())\"",
            shell=True,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            count = result.stdout.strip()
            print_success(f"{table}: {count} records")
    
    return True


def cleanup():
    """Clean up temporary files."""
    print_header("Cleanup")
    
    response = input("Do you want to remove the data dump file? (y/n): ")
    if response.lower() == 'y':
        try:
            Path('data_dump.json').unlink()
            print_success("data_dump.json removed")
        except Exception as e:
            print_warning(f"Could not remove data_dump.json: {e}")


def main():
    """Main migration process."""
    print_header("SQLite to PostgreSQL Migration Tool")
    print_info("This script will migrate your data from SQLite to PostgreSQL")
    print_warning("Make sure to backup your database before proceeding!\n")
    
    response = input("Do you want to continue? (y/n): ")
    if response.lower() != 'y':
        print_info("Migration cancelled.")
        return
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print_error("Prerequisites check failed. Exiting.")
        return
    
    # Step 2: Backup SQLite database
    if not backup_sqlite():
        print_error("Backup failed. Exiting.")
        return
    
    # Step 3: Dump data from SQLite
    if not dump_sqlite_data():
        print_error("Data dump failed. Exiting.")
        return
    
    # Step 4: Setup PostgreSQL database
    if not setup_postgresql_db():
        print_error("PostgreSQL setup incomplete. Exiting.")
        return
    
    # Step 5: Run migrations on PostgreSQL
    if not migrate_postgresql():
        print_error("Migration failed. Exiting.")
        return
    
    # Step 6: Load data into PostgreSQL
    if not load_data_to_postgresql():
        print_error("Data loading failed. Exiting.")
        return
    
    # Step 7: Verify data
    verify_data()
    
    # Step 8: Cleanup
    cleanup()
    
    # Final message
    print_header("Migration Complete!")
    print_success("Your data has been successfully migrated to PostgreSQL!")
    print_info("\nNext steps:")
    print_info("1. Update your .env file: USE_POSTGRES=True")
    print_info("2. Test your application thoroughly")
    print_info("3. Keep the SQLite backup until you're confident everything works")
    print_info("4. Consider setting up regular PostgreSQL backups\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n\nMigration interrupted by user. Exiting.")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
