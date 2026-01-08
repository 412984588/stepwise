#!/usr/bin/env bash
# dev_up.sh - Start StepWise development servers
# Usage: ./scripts/dev_up.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting StepWise development environment...${NC}"

# Export dev environment variables
export API_ACCESS_KEY="${API_ACCESS_KEY:-dev-test-key}"
export EMAIL_PROVIDER="${EMAIL_PROVIDER:-console}"
export DATABASE_URL="${DATABASE_URL:-sqlite:///./stepwise.db}"
export DEBUG="${DEBUG:-true}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"

echo -e "${YELLOW}📋 Environment:${NC}"
echo "   API_ACCESS_KEY: ${API_ACCESS_KEY:0:8}..."
echo "   EMAIL_PROVIDER: $EMAIL_PROVIDER"
echo "   DATABASE_URL: $DATABASE_URL"

# Create PID directory
PID_DIR="$PROJECT_ROOT/.pids"
mkdir -p "$PID_DIR"

# Check if servers are already running
if [ -f "$PID_DIR/backend.pid" ] && kill -0 "$(cat "$PID_DIR/backend.pid")" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Backend already running (PID $(cat "$PID_DIR/backend.pid"))${NC}"
else
    echo -e "${GREEN}🔧 Starting backend on port 8000...${NC}"
    cd "$PROJECT_ROOT/backend"

    # Start backend in background
    uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$PID_DIR/backend.pid"
    echo -e "${GREEN}   Backend PID: $BACKEND_PID${NC}"
fi

if [ -f "$PID_DIR/frontend.pid" ] && kill -0 "$(cat "$PID_DIR/frontend.pid")" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Frontend already running (PID $(cat "$PID_DIR/frontend.pid"))${NC}"
else
    echo -e "${GREEN}🎨 Starting frontend on port 3000...${NC}"
    cd "$PROJECT_ROOT/frontend"

    # Start frontend in background
    npm run dev -- --host 127.0.0.1 --port 3000 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$PID_DIR/frontend.pid"
    echo -e "${GREEN}   Frontend PID: $FRONTEND_PID${NC}"
fi

# Wait a moment for servers to start
sleep 2

echo ""
echo -e "${GREEN}✅ Development servers started!${NC}"
echo ""
echo "   Backend:  http://127.0.0.1:8000"
echo "   Frontend: http://127.0.0.1:3000"
echo "   API Docs: http://127.0.0.1:8000/docs"
echo ""
echo -e "${YELLOW}💡 To stop servers: ./scripts/dev_down.sh${NC}"
echo ""

# Keep script running if started directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo -e "${YELLOW}Press Ctrl+C to stop all servers...${NC}"
    trap "$SCRIPT_DIR/dev_down.sh; exit 0" SIGINT SIGTERM
    wait
fi
