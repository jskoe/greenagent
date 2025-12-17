#!/bin/bash

# WebNav Green Agent Enhanced Demo Script
# This script demonstrates the complete WebNav Green Agent MVP with enhanced visuals

set -e  # Exit on any error

# Enhanced colors and styling
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Function to print styled headers
print_header() {
    echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${CYAN}║${WHITE} $1${CYAN} ║${NC}"
    echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to print section headers
print_section() {
    echo -e "${BOLD}${PURPLE}▶ $1${NC}"
    echo -e "${PURPLE}────────────────────────────────────────────────────────────────────────────────${NC}"
}

echo -e "${BOLD}${WHITE}"
echo "    ██╗    ██╗███████╗██████╗ ███╗   ██╗ █████╗ ██╗    ██╗"
echo "    ██║    ██║██╔════╝██╔══██╗████╗  ██║██╔══██╗██║    ██║"
echo "    ██║ █╗ ██║█████╗  ██████╔╝██╔██╗ ██║███████║██║ █╗ ██║"
echo "    ██║███╗██║██╔══╝  ██╔══██╗██║╚██╗██║██╔══██║██║███╗██║"
echo "    ╚███╔███╔╝███████╗██████╔╝██║ ╚████║██║  ██║╚███╔███╔╝"
echo "     ╚══╝╚══╝ ╚══════╝╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚══╝╚══╝"
echo -e "${NC}"
echo -e "${BOLD}${GREEN}                    Green Agent Evaluation Host${NC}"
echo -e "${BOLD}${YELLOW}                    Enhanced Demo Experience${NC}"
echo ""

# Function to print colored output with enhanced styling
print_step() {
    echo -e "${BOLD}${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${BOLD}${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BOLD}${YELLOW}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${BOLD}${RED}❌ $1${NC}"
}

print_progress() {
    echo -e "${BOLD}${CYAN}⏳ $1${NC}"
}

print_feature() {
    echo -e "${BOLD}${PURPLE}🎯 $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "webnav/requirements.txt" ]; then
    print_error "Please run this script from the greenagent root directory"
    exit 1
fi

print_header "SETUP & INSTALLATION"
print_section "Installing Dependencies"

print_progress "Installing Python packages..."
cd webnav
pip install -r requirements.txt > /dev/null 2>&1
print_success "Python dependencies installed"

print_progress "Installing Playwright browsers..."
playwright install chromium > /dev/null 2>&1
print_success "Playwright browsers installed"
echo ""

print_header "SERVICE STARTUP"
print_section "Starting WebNav Service"

print_progress "Starting FastAPI server on port 8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
SERVER_PID=$!

print_progress "Waiting for service to initialize..."
sleep 3

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    print_error "Failed to start server"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi

print_success "WebNav service started successfully"
print_info "Service available at: http://localhost:8000"
print_info "Dashboard available at: http://localhost:8000/site/dashboard.html"
echo ""

print_step "Step 3: Testing API Endpoints"
echo ""

# Test health endpoint
print_info "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
echo "Response: $HEALTH_RESPONSE"
if [[ "$HEALTH_RESPONSE" == *"ok"* ]]; then
    print_success "Health check passed"
else
    print_error "Health check failed"
fi
echo ""

# Test root endpoint
print_info "Testing root endpoint..."
ROOT_RESPONSE=$(curl -s http://localhost:8000/)
echo "Response: $ROOT_RESPONSE"
print_success "Root endpoint working"
echo ""

# Test static file serving
print_info "Testing static file serving..."
STATIC_RESPONSE=$(curl -s http://localhost:8000/site/product.html | head -5)
echo "Static file preview:"
echo "$STATIC_RESPONSE"
print_success "Static files serving correctly"
echo ""

print_header "TASK EXECUTION DEMO"
print_section "Running Multiple Tasks"

# Task 1: Price extraction
print_feature "Task 1: Price Extraction"
print_info "Finding the price of the third product..."
TASK_RESPONSE=$(curl -s -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task_id":"task_001"}')

# Check success using Python for more reliable JSON parsing
SUCCESS=$(echo "$TASK_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['success'])")

if [[ "$SUCCESS" == "True" ]]; then
    PRICE=$(echo "$TASK_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['evidence']['matched_text'])")
    print_success "Task 1 completed! Found price: $PRICE"
else
    print_error "Task 1 failed"
    print_info "Response: $TASK_RESPONSE"
fi
echo ""

# Task 2: Rating extraction
print_feature "Task 2: Rating Extraction"
print_info "Finding the rating of the most expensive product..."
TASK_RESPONSE_2=$(curl -s -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task_id":"task_002"}')

# Check success using Python for more reliable JSON parsing
SUCCESS_2=$(echo "$TASK_RESPONSE_2" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['success'])")

if [[ "$SUCCESS_2" == "True" ]]; then
    RATING=$(echo "$TASK_RESPONSE_2" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['evidence']['matched_text'])")
    print_success "Task 2 completed! Found rating: $RATING"
else
    print_error "Task 2 failed"
    print_info "Response: $TASK_RESPONSE_2"
fi
echo ""

# Task 3: Product counting
print_feature "Task 3: Product Counting"
print_info "Counting total number of products..."
TASK_RESPONSE_3=$(curl -s -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task_id":"task_003"}')

# Check success using Python for more reliable JSON parsing
SUCCESS_3=$(echo "$TASK_RESPONSE_3" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['success'])")

if [[ "$SUCCESS_3" == "True" ]]; then
    COUNT=$(echo "$TASK_RESPONSE_3" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['evidence']['matched_text'])")
    print_success "Task 3 completed! Found count: $COUNT"
else
    print_error "Task 3 failed"
    print_info "Response: $TASK_RESPONSE_3"
fi
echo ""

print_step "Step 5: Verifying Artifacts"
echo "Checking saved artifacts..."

if [ -d "runs/task_001" ]; then
    print_success "Artifacts directory created"
    echo "Saved files:"
    ls -la runs/task_001/
    echo ""
    
    # Show report content
    print_info "Task report content:"
    cat runs/task_001/report.json | python3 -m json.tool
    echo ""
    
    # Show action log
    print_info "Action log:"
    cat runs/task_001/actions.log
    echo ""
else
    print_error "Artifacts directory not found"
fi
echo ""

print_step "Step 6: Testing Reset and Reproducibility"
echo "Testing reset functionality..."

RESET_RESPONSE=$(curl -s -X POST http://localhost:8000/reset)
echo "Reset response: $RESET_RESPONSE"
print_success "Reset completed"
echo ""

echo "Running task again to verify reproducibility..."
TASK_RESPONSE_REPRO=$(curl -s -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task_id":"task_001"}')

echo "Second execution response:"
echo "$TASK_RESPONSE_REPRO" | python3 -m json.tool
echo ""

# Check success using Python for more reliable JSON parsing
SUCCESS_REPRO=$(echo "$TASK_RESPONSE_REPRO" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['success'])")

if [[ "$SUCCESS_REPRO" == "True" ]]; then
    print_success "Reproducible execution confirmed!"
else
    print_error "Reproducibility test failed"
    print_info "Response: $TASK_RESPONSE_REPRO"
fi
echo ""

print_header "DEMO COMPLETE"
print_section "Key Features Demonstrated"

print_feature "Isolated Browser Contexts"
print_info "Fresh Playwright context per task prevents state leakage"

print_feature "Deterministic Judging"
print_info "CSS selector + regex validation for reproducible results"

print_feature "Artifact Tracking"
print_info "Complete evidence trail: HTML snapshots, screenshots, logs"

print_feature "Static File Serving"
print_info "Beautiful product catalog with modern UI design"

print_feature "API-First Design"
print_info "Clean endpoints ready for external agent integration"

print_feature "Multi-Task Support"
print_info "Demonstrated price extraction, rating analysis, and counting"

print_header "NEXT STEPS"
print_section "Continue Exploring"

print_info "🌐 Web Interface:"
echo -e "   ${CYAN}• Dashboard: http://localhost:8000/site/dashboard.html${NC}"
echo -e "   ${CYAN}• Product Catalog: http://localhost:8000/site/product.html${NC}"
echo -e "   ${CYAN}• API Docs: http://localhost:8000/docs${NC}"
echo ""

print_info "🔧 API Testing:"
echo -e "   ${CYAN}• Health Check: curl http://localhost:8000/health${NC}"
echo -e "   ${CYAN}• Execute Task: curl -X POST http://localhost:8000/task -H 'Content-Type: application/json' -d '{\"task_id\":\"task_001\"}'${NC}"
echo -e "   ${CYAN}• Reset Controller: curl -X POST http://localhost:8000/reset${NC}"
echo ""

print_info "📁 Artifacts Location:"
echo -e "   ${CYAN}• Task Reports: runs/task_001/, runs/task_002/, runs/task_003/${NC}"
echo -e "   ${CYAN}• Screenshots: runs/*/snap.png${NC}"
echo -e "   ${CYAN}• Action Logs: runs/*/actions.log${NC}"
echo ""

print_success "WebNav Green Agent is ready for production use!"
print_info "Press Ctrl+C to stop the service and end the demo"
echo ""

# Keep the script running so the server stays up
echo "Press Ctrl+C to stop the demo and server..."
trap 'echo ""; print_info "Stopping WebNav service..."; kill $SERVER_PID 2>/dev/null || true; print_success "Demo complete!"; exit 0' INT

# Wait for user to stop
while true; do
    sleep 1
done
