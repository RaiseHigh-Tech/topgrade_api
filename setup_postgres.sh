#!/bin/bash

# Script to setup PostgreSQL database for the project
# This script should be run with appropriate PostgreSQL privileges

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}PostgreSQL Database Setup Script${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Detect OS
OS_TYPE="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macos"
    echo -e "${BLUE}Detected: macOS${NC}\n"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="linux"
    echo -e "${BLUE}Detected: Linux${NC}\n"
else
    echo -e "${YELLOW}⚠ Unknown OS: $OSTYPE${NC}\n"
fi

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✓ Loaded environment variables from .env${NC}"
else
    echo -e "${YELLOW}⚠ .env file not found. Using default values.${NC}"
    DB_NAME="topgrade_db"
    DB_USER="topgrade_user"
    DB_PASSWORD="topgrade_password"
fi

echo -e "\n${BLUE}Database Configuration:${NC}"
echo -e "  Database Name: ${DB_NAME}"
echo -e "  Database User: ${DB_USER}"
echo -e "  Database Password: ${DB_PASSWORD}\n"

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}✗ PostgreSQL is not installed!${NC}"
    echo -e "${YELLOW}Please install PostgreSQL first:${NC}"
    echo -e "  Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    echo -e "  CentOS/RHEL:   sudo yum install postgresql-server postgresql-contrib"
    echo -e "  macOS:         brew install postgresql"
    exit 1
fi

echo -e "${GREEN}✓ PostgreSQL is installed${NC}"

# Get PostgreSQL version
PG_VERSION=$(psql --version | awk '{print $3}')
echo -e "${BLUE}PostgreSQL Version: ${PG_VERSION}${NC}\n"

# Check if PostgreSQL is running and start if needed
PG_RUNNING=false

if [ "$OS_TYPE" == "macos" ]; then
    # macOS with Homebrew
    # Try different PostgreSQL service names
    if brew services list | grep -q "postgresql@17.*started"; then
        PG_RUNNING=true
        PG_SERVICE="postgresql@17"
    elif brew services list | grep -q "postgresql@16.*started"; then
        PG_RUNNING=true
        PG_SERVICE="postgresql@16"
    elif brew services list | grep -q "postgresql@15.*started"; then
        PG_RUNNING=true
        PG_SERVICE="postgresql@15"
    elif brew services list | grep -q "postgresql@14.*started"; then
        PG_RUNNING=true
        PG_SERVICE="postgresql@14"
    elif brew services list | grep -q "postgresql.*started"; then
        PG_RUNNING=true
        PG_SERVICE="postgresql"
    fi

    if [ "$PG_RUNNING" = true ]; then
        echo -e "${GREEN}✓ PostgreSQL service ($PG_SERVICE) is running${NC}\n"
    else
        echo -e "${YELLOW}⚠ PostgreSQL service is not running${NC}"
        echo -e "${BLUE}Attempting to start PostgreSQL...${NC}"
        
        # Try to detect installed PostgreSQL version
        if brew list | grep -q "postgresql@17"; then
            PG_SERVICE="postgresql@17"
        elif brew list | grep -q "postgresql@16"; then
            PG_SERVICE="postgresql@16"
        elif brew list | grep -q "postgresql@15"; then
            PG_SERVICE="postgresql@15"
        elif brew list | grep -q "postgresql@14"; then
            PG_SERVICE="postgresql@14"
        elif brew list | grep -q "postgresql"; then
            PG_SERVICE="postgresql"
        else
            echo -e "${RED}✗ Cannot detect PostgreSQL installation${NC}"
            exit 1
        fi
        
        brew services start $PG_SERVICE
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ PostgreSQL service ($PG_SERVICE) started successfully${NC}\n"
            sleep 2  # Give it a moment to start
        else
            echo -e "${RED}✗ Failed to start PostgreSQL service${NC}"
            echo -e "${YELLOW}Please start it manually: brew services start $PG_SERVICE${NC}"
            exit 1
        fi
    fi
    
    # Set PGUSER for macOS (usually the current user)
    PGUSER="${USER}"
    
elif [ "$OS_TYPE" == "linux" ]; then
    # Linux with systemd
    if sudo systemctl is-active --quiet postgresql; then
        PG_RUNNING=true
        echo -e "${GREEN}✓ PostgreSQL service is running${NC}\n"
    else
        echo -e "${YELLOW}⚠ PostgreSQL service is not running${NC}"
        echo -e "${BLUE}Attempting to start PostgreSQL...${NC}"
        sudo systemctl start postgresql
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ PostgreSQL service started successfully${NC}\n"
        else
            echo -e "${RED}✗ Failed to start PostgreSQL service${NC}"
            echo -e "${YELLOW}Please start it manually: sudo systemctl start postgresql${NC}"
            exit 1
        fi
    fi
    
    # Set PGUSER for Linux (usually postgres)
    PGUSER="postgres"
fi

# Create database and user
echo -e "${BLUE}Creating database and user...${NC}\n"

if [ "$OS_TYPE" == "macos" ]; then
    # macOS - run psql as current user
    psql -U ${PGUSER} postgres << EOF
-- Create database
DROP DATABASE IF EXISTS ${DB_NAME};
CREATE DATABASE ${DB_NAME};

-- Create user (only if not exists)
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
    CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
  ELSE
    ALTER USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
  END IF;
END
\$\$;

-- Grant privileges
ALTER ROLE ${DB_USER} SET client_encoding TO 'utf8';
ALTER ROLE ${DB_USER} SET default_transaction_isolation TO 'read committed';
ALTER ROLE ${DB_USER} SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};

-- Connect to the database and grant schema privileges
\c ${DB_NAME}

-- For PostgreSQL 15+, grant schema privileges
GRANT ALL ON SCHEMA public TO ${DB_USER};
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${DB_USER};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${DB_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${DB_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${DB_USER};

\q
EOF

elif [ "$OS_TYPE" == "linux" ]; then
    # Linux - run psql as postgres user
    sudo -u postgres psql << EOF
-- Create database
DROP DATABASE IF EXISTS ${DB_NAME};
CREATE DATABASE ${DB_NAME};

-- Create user
DROP USER IF EXISTS ${DB_USER};
CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';

-- Grant privileges
ALTER ROLE ${DB_USER} SET client_encoding TO 'utf8';
ALTER ROLE ${DB_USER} SET default_transaction_isolation TO 'read committed';
ALTER ROLE ${DB_USER} SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};

-- For PostgreSQL 15+, grant schema privileges
\c ${DB_NAME}
GRANT ALL ON SCHEMA public TO ${DB_USER};
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${DB_USER};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${DB_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${DB_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${DB_USER};

\q
EOF

else
    echo -e "${RED}✗ Unsupported operating system${NC}"
    exit 1
fi

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ Database and user created successfully!${NC}\n"
    
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}Setup Complete!${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    
    echo -e "${YELLOW}Next steps:${NC}"
    echo -e "  1. Update your .env file with:"
    echo -e "     USE_POSTGRES=True"
    echo -e "     DB_NAME=${DB_NAME}"
    echo -e "     DB_USER=${DB_USER}"
    echo -e "     DB_PASSWORD=${DB_PASSWORD}"
    echo -e "     DB_HOST=localhost"
    echo -e "     DB_PORT=5432"
    echo -e ""
    echo -e "  2. Install PostgreSQL adapter:"
    echo -e "     pip install psycopg2-binary"
    echo -e ""
    echo -e "  3. Run migrations:"
    echo -e "     python manage.py migrate"
    echo -e ""
    echo -e "  4. To migrate existing SQLite data:"
    echo -e "     python migrate_sqlite_to_postgres.py"
    echo -e ""
    
    if [ "$OS_TYPE" == "macos" ]; then
        echo -e "${BLUE}macOS PostgreSQL Commands:${NC}"
        echo -e "  Start:   brew services start ${PG_SERVICE}"
        echo -e "  Stop:    brew services stop ${PG_SERVICE}"
        echo -e "  Restart: brew services restart ${PG_SERVICE}"
        echo -e "  Status:  brew services list | grep postgresql"
        echo -e ""
    fi
else
    echo -e "\n${RED}✗ Failed to create database and user${NC}"
    echo -e "${YELLOW}Please check PostgreSQL logs for errors${NC}"
    
    if [ "$OS_TYPE" == "macos" ]; then
        echo -e "\n${BLUE}Troubleshooting on macOS:${NC}"
        echo -e "  Check logs: brew services info ${PG_SERVICE}"
        echo -e "  Or check: tail -f /opt/homebrew/var/log/${PG_SERVICE}.log"
        echo -e "  Connect manually: psql postgres"
    fi
    exit 1
fi
