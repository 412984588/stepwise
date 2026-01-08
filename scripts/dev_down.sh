#!/usr/bin/env bash
# dev_down.sh - Stop StepWise development servers
# Usage: ./scripts/dev_down.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Stopping StepWise development servers...${NC}"

PID_DIR="$PROJECT_ROOT/.pids"

# Stop backend
if [ -f "$PID_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$PID_DIR/backend.pid")
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo -e "${YELLOW}   Stopping backend (PID $BACKEND_PID)...${NC}"
        kill "$BACKEND_PID" 2>/dev/null || true
        # Wait for graceful shutdown
        sleep 1
        # Force kill if still running
        kill -9 "$BACKEND_PID" 2>/dev/null || true
        echo -e "${GREEN}   ✓ Backend stopped${NC}"
    else
        echo -e "${YELLOW}   Backend not running${NC}"
    fi
    rm -f "$PID_DIR/backend.pid"
else
    echo -e "${YELLOW}   No backend PID file found${NC}"
fi

# Stop frontend
if [ -f "$PID_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PID_DIR/frontend.pid")
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo -e "${YELLOW}   Stopping frontend (PID $FRONTEND_PID)...${NC}"
        kill "$FRONTEND_PID" 2>/dev/null || true
        # Wait for graceful shutdown
        sleep 1
        # Force kill if still running
        kill -9 "$FRONTEND_PID" 2>/dev/null || true
        echo -e "${GREEN}   ✓ Frontend stopped${NC}"
    else
        echo -e "${YELLOW}   Frontend not running${NC}"
    fi
    rm -f "$PID_DIR/frontend.pid"
else
    echo -e "${YELLOW}   No frontend PID file found${NC}"
fi

# Also kill any stray uvicorn/vite processes on our ports
echo -e "${YELLOW}   Cleaning up stray processes...${NC}"

# Kill processes on port 8000 (backend)
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null || true

# Kill processes on port 3000 (frontend)
lsof -ti:3000 2>/dev/null | xargs kill -9 2>/dev/null || true

echo ""
echo -e "${GREEN}✅ All servers stopped${NC}"
