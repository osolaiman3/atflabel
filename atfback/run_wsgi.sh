#!/bin/bash
# Quick start script for running the ATF Label application with Gunicorn

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ATF Label Application - Gunicorn     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}\n"

# Check if in correct directory
if [ ! -f "wsgi.py" ]; then
    echo -e "${RED}Error: wsgi.py not found${NC}"
    echo -e "${YELLOW}Please run this script from the atfback directory:${NC}"
    echo "  cd atfback && bash run_wsgi.sh"
    exit 1
fi

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python not found${NC}"
    exit 1
fi

# # Build React frontend
# echo -e "${GREEN}Building React frontend...${NC}"
# if [ -d "../atffront" ]; then
#     cd ../atffront
    
#     if [ ! -d "node_modules" ]; then
#         echo -e "${YELLOW}Installing npm dependencies...${NC}"
#         npm install
#     fi
    
#     echo -e "${YELLOW}Building React app...${NC}"
#     npm run build
    
#     if [ ! -d "build" ]; then
#         echo -e "${RED}Error: React build failed${NC}"
#         exit 1
#     fi
    
#     echo -e "${GREEN}✓ React build complete${NC}\n"
#     cd ../atfback
# else
#     echo -e "${RED}Error: ../atffront directory not found${NC}"
#     exit 1
# fi

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}Loading environment from .env file...${NC}"
    export $(grep -v '^#' .env | xargs)
fi

# python src/server.py

# Get configuration from environment or use defaults
WORKERS=${GUNICORN_WORKERS:-1}
BIND=${GUNICORN_BIND:-0.0.0.0:10000}
TIMEOUT=${GUNICORN_TIMEOUT:-120}
LOGLEVEL=${GUNICORN_LOGLEVEL:-info}

echo -e "${GREEN}Configuration:${NC}"
echo "  Workers:    $WORKERS"
echo "  Bind:       $BIND"
echo "  Timeout:    ${TIMEOUT}s"
echo "  Log Level:  $LOGLEVEL"
echo ""

# Check if gunicorn is installed
if ! python -c "import gunicorn" 2>/dev/null; then
    echo -e "${YELLOW}Gunicorn not found. Installing dependencies...${NC}"
    pip install -r requirements.txt
fi

# Start Gunicorn
echo -e "${GREEN}Starting ATF Label Server...${NC}\n"
exec gunicorn \
    -w "$WORKERS" \
    -b "$BIND" \
    --timeout "$TIMEOUT" \
    --log-level "$LOGLEVEL" \
    --access-logfile - \
    --error-logfile - \
    wsgi:app
