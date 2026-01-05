#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Video Tools Application...${NC}"

# Function to kill background processes on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit
}

# Set up trap to call cleanup function on script exit
trap cleanup EXIT INT TERM

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed${NC}"
    exit 1
fi

# Setup virtual environment for backend
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment and install dependencies
echo -e "${YELLOW}Activating virtual environment...${NC}"
source backend/venv/bin/activate

# Install backend dependencies if needed
if ! pip show uvicorn &> /dev/null; then
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    cd backend
    pip install -r requirements.txt
    cd ..
fi

# Check if frontend exists and has node_modules
if [ -d "frontend" ]; then
    if [ ! -d "frontend/node_modules" ]; then
        echo -e "${YELLOW}Frontend dependencies not found. Installing...${NC}"
        cd frontend && npm install && cd ..
    fi
    FRONTEND_EXISTS=true
else
    echo -e "${YELLOW}Frontend directory not found, will run backend only${NC}"
    FRONTEND_EXISTS=false
fi

# Start backend
echo -e "${GREEN}Starting backend server on port 8009...${NC}"
cd backend
python -m uvicorn app.main:app --reload --port 8009 --timeout-keep-alive 3600 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend if it exists
if [ "$FRONTEND_EXISTS" = true ]; then
    echo -e "${GREEN}Starting frontend server on port 5173...${NC}"
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..

    echo -e "${GREEN}✓ Backend running at: http://localhost:8009${NC}"
    echo -e "${GREEN}✓ Frontend running at: http://localhost:5173${NC}"
else
    echo -e "${GREEN}✓ Backend running at: http://localhost:8009${NC}"
fi

echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for background processes
wait