#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== StepWise Staging Deployment ===${NC}"
echo ""

if ! command -v fly &> /dev/null; then
    echo -e "${RED}Error: Fly CLI not installed${NC}"
    echo "Install with: brew install flyctl"
    exit 1
fi

if ! fly auth whoami &> /dev/null; then
    echo -e "${YELLOW}Not logged in to Fly.io. Starting login...${NC}"
    fly auth login
fi

echo -e "${GREEN}Logged in as: $(fly auth whoami)${NC}"
echo ""

echo -e "${YELLOW}Step 1: Creating backend app...${NC}"
cd "$PROJECT_ROOT/backend"
if fly apps list | grep -q "stepwise-backend-staging"; then
    echo "App stepwise-backend-staging already exists"
else
    fly apps create stepwise-backend-staging --org personal
fi

echo -e "${YELLOW}Step 2: Creating persistent volume for SQLite...${NC}"
if fly volumes list -a stepwise-backend-staging | grep -q "stepwise_data"; then
    echo "Volume stepwise_data already exists"
else
    fly volumes create stepwise_data --region sjc --size 1 -a stepwise-backend-staging
fi

echo -e "${YELLOW}Step 3: Setting backend secrets...${NC}"
echo "You'll be prompted to enter secrets (press Enter to skip if already set)"

read -p "Enter BETA_ACCESS_CODE (or press Enter to skip): " BETA_CODE
if [ -n "$BETA_CODE" ]; then
    fly secrets set BETA_ACCESS_CODE="$BETA_CODE" -a stepwise-backend-staging
fi

read -p "Enter OPENAI_API_KEY (or press Enter to skip): " OPENAI_KEY
if [ -n "$OPENAI_KEY" ]; then
    fly secrets set OPENAI_API_KEY="$OPENAI_KEY" -a stepwise-backend-staging
fi

fly secrets set ALLOWED_ORIGINS="https://stepwise-frontend-staging.fly.dev,http://localhost:3000" -a stepwise-backend-staging

echo -e "${YELLOW}Step 4: Deploying backend...${NC}"
fly deploy -a stepwise-backend-staging

echo -e "${GREEN}Backend deployed!${NC}"
BACKEND_URL="https://stepwise-backend-staging.fly.dev"
echo "Backend URL: $BACKEND_URL"
echo ""

echo -e "${YELLOW}Step 5: Creating frontend app...${NC}"
cd "$PROJECT_ROOT/frontend"
if fly apps list | grep -q "stepwise-frontend-staging"; then
    echo "App stepwise-frontend-staging already exists"
else
    fly apps create stepwise-frontend-staging --org personal
fi

echo -e "${YELLOW}Step 6: Deploying frontend...${NC}"
fly deploy -a stepwise-frontend-staging --build-arg VITE_API_BASE_URL="$BACKEND_URL"

echo -e "${GREEN}Frontend deployed!${NC}"
FRONTEND_URL="https://stepwise-frontend-staging.fly.dev"
echo "Frontend URL: $FRONTEND_URL"
echo ""

echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
echo "Backend:  $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
echo "API Docs: $BACKEND_URL/docs"
echo ""
echo -e "${YELLOW}To verify beta gate:${NC}"
echo "1. Open $FRONTEND_URL"
echo "2. You should see the beta gate modal"
echo "3. Enter your BETA_ACCESS_CODE to proceed"
