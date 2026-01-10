#!/usr/bin/env bash
#
# run_local_qa.sh - Automated Local QA Testing Script
#
# This script automates the local QA testing workflow:
# 1. Starts PostgreSQL via docker-compose
# 2. Runs backend tests (pytest)
# 3. Runs frontend E2E tests (Playwright)
# 4. Opens Playwright UI for exploratory testing
#
# Usage:
#   ./scripts/run_local_qa.sh [--skip-docker] [--skip-tests] [--ui-only]
#
# Options:
#   --skip-docker   Skip starting docker-compose (assumes PostgreSQL already running)
#   --skip-tests    Skip automated tests, go straight to Playwright UI
#   --ui-only       Only open Playwright UI (skip everything else)
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
SKIP_DOCKER=false
SKIP_TESTS=false
UI_ONLY=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-docker)
            SKIP_DOCKER=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --ui-only)
            UI_ONLY=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the project root
if [ ! -f "docker-compose.dev.yml" ] && [ ! -f "docker-compose.yml" ]; then
    log_error "Must run from project root directory"
    exit 1
fi

# Determine which docker-compose file to use
COMPOSE_FILE="docker-compose.yml"
if [ -f "docker-compose.dev.yml" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
fi

# Step 1: Start PostgreSQL (unless skipped or UI-only)
if [ "$UI_ONLY" = false ] && [ "$SKIP_DOCKER" = false ]; then
    log_info "Starting PostgreSQL via docker-compose..."

    # Check if PostgreSQL is already running
    if docker-compose -f "$COMPOSE_FILE" ps postgres | grep -q "Up"; then
        log_warning "PostgreSQL is already running"
    else
        docker-compose -f "$COMPOSE_FILE" --profile postgres up -d

        # Wait for PostgreSQL to be ready
        log_info "Waiting for PostgreSQL to be ready..."
        sleep 5

        # Health check
        until docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U stepwise_user -d stepwise_db > /dev/null 2>&1; do
            echo -n "."
            sleep 1
        done
        echo ""
        log_success "PostgreSQL is ready"
    fi
fi

# Step 2: Run backend tests (unless skipped or UI-only)
if [ "$UI_ONLY" = false ] && [ "$SKIP_TESTS" = false ]; then
    log_info "Running backend tests (pytest)..."

    cd backend

    # Check if virtual environment exists
    if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
        log_warning "No virtual environment found. Creating one..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -e ".[dev]"
    else
        # Activate existing venv
        if [ -d "venv" ]; then
            source venv/bin/activate
        else
            source .venv/bin/activate
        fi
    fi

    # Run pytest with coverage
    log_info "Running pytest with coverage..."
    PYTHONPATH=$(pwd) pytest tests/ -v --cov=. --cov-report=term-missing

    if [ $? -eq 0 ]; then
        log_success "Backend tests passed"
    else
        log_error "Backend tests failed"
        exit 1
    fi

    cd ..
fi

# Step 3: Run frontend E2E tests (unless skipped or UI-only)
if [ "$UI_ONLY" = false ] && [ "$SKIP_TESTS" = false ]; then
    log_info "Running frontend E2E tests (Playwright)..."

    cd frontend

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log_warning "node_modules not found. Running npm install..."
        npm install
    fi

    # Install Playwright browsers if needed
    if [ ! -d "$HOME/.cache/ms-playwright" ]; then
        log_info "Installing Playwright browsers..."
        npx playwright install --with-deps
    fi

    # Start backend server in background
    log_info "Starting backend server..."
    cd ../backend
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        source .venv/bin/activate
    fi

    # Kill any existing backend server on port 8000
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true

    uvicorn backend.main:app --host 0.0.0.0 --port 8000 > /tmp/stepwise_backend.log 2>&1 &
    BACKEND_PID=$!

    # Wait for backend to be ready
    log_info "Waiting for backend to be ready..."
    sleep 3
    until curl -s http://localhost:8000/health > /dev/null 2>&1; do
        echo -n "."
        sleep 1
    done
    echo ""
    log_success "Backend is ready (PID: $BACKEND_PID)"

    # Start frontend dev server in background
    log_info "Starting frontend dev server..."
    cd ../frontend

    # Kill any existing frontend server on port 3000
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true

    npm run dev > /tmp/stepwise_frontend.log 2>&1 &
    FRONTEND_PID=$!

    # Wait for frontend to be ready
    log_info "Waiting for frontend to be ready..."
    sleep 5
    until curl -s http://localhost:3000 > /dev/null 2>&1; do
        echo -n "."
        sleep 1
    done
    echo ""
    log_success "Frontend is ready (PID: $FRONTEND_PID)"

    # Run Playwright tests with xvfb (headless)
    log_info "Running Playwright E2E tests..."

    # Check if running on Linux (need xvfb)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Install xvfb if not present
        if ! command -v xvfb-run &> /dev/null; then
            log_warning "xvfb not found. Install with: sudo apt-get install xvfb"
        fi
        xvfb-run npx playwright test
    else
        # macOS/Windows - run without xvfb
        npx playwright test
    fi

    PLAYWRIGHT_EXIT_CODE=$?

    # Kill background servers
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true

    if [ $PLAYWRIGHT_EXIT_CODE -eq 0 ]; then
        log_success "Playwright E2E tests passed"
    else
        log_error "Playwright E2E tests failed"
        log_info "Check logs:"
        log_info "  Backend: /tmp/stepwise_backend.log"
        log_info "  Frontend: /tmp/stepwise_frontend.log"
        exit 1
    fi

    cd ..
fi

# Step 4: Open Playwright UI for exploratory testing
log_info "Opening Playwright UI for exploratory testing..."

cd frontend

# Start backend server if not already running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    log_info "Starting backend server..."
    cd ../backend
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        source .venv/bin/activate
    fi

    # Kill any existing backend server
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true

    uvicorn backend.main:app --host 0.0.0.0 --port 8000 > /tmp/stepwise_backend.log 2>&1 &
    BACKEND_PID=$!

    sleep 3
    log_success "Backend is ready (PID: $BACKEND_PID)"
    cd ../frontend
fi

# Start frontend dev server if not already running
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    log_info "Starting frontend dev server..."

    # Kill any existing frontend server
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true

    npm run dev > /tmp/stepwise_frontend.log 2>&1 &
    FRONTEND_PID=$!

    sleep 5
    log_success "Frontend is ready (PID: $FRONTEND_PID)"
fi

# Open Playwright UI
log_success "Opening Playwright UI..."
log_info "You can now:"
log_info "  1. Run tests interactively"
log_info "  2. Debug failing tests"
log_info "  3. Explore the application manually"
log_info ""
log_info "Press Ctrl+C to stop servers when done"

npx playwright test --ui

# Cleanup on exit
cleanup() {
    log_info "Cleaning up..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    log_success "Cleanup complete"
}

trap cleanup EXIT
