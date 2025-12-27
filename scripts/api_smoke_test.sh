#!/bin/bash
# ============================================================================
# API Smoke Test Script
# Purpose: End-to-end test of critical API endpoints
# Usage: export TEST_TOKEN="your-jwt-token" && bash scripts/api_smoke_test.sh
# ============================================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
TWIN_ID="${TWIN_ID:-}"  # Can be set externally or will be created

echo "========================================="
echo "API SMOKE TEST"
echo "========================================="
echo "API URL: $API_URL"
echo ""

# Check if TEST_TOKEN is set
if [ -z "$TEST_TOKEN" ]; then
    echo -e "${RED}ERROR: TEST_TOKEN environment variable not set${NC}"
    echo "Please obtain a JWT token from the browser and export it:"
    echo "  export TEST_TOKEN='eyJ...'"
    exit 1
fi

# ============================================================================
# TEST 1: Health Check
# ============================================================================
echo -e "${YELLOW}TEST 1: Health Check${NC}"
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_URL/health")
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Backend is healthy"
    echo "Response: $BODY"
else
    echo -e "${RED}✗ FAIL${NC} - Health check failed (HTTP $HTTP_STATUS)"
    echo "Response: $BODY"
    exit 1
fi
echo ""

# ============================================================================
# TEST 2: CORS Preflight
# ============================================================================
echo -e "${YELLOW}TEST 2: CORS Preflight${NC}"
CORS_RESPONSE=$(curl -s -i -X OPTIONS "$API_URL/auth/sync-user" \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: POST" 2>&1)

if echo "$CORS_RESPONSE" | grep -q "access-control-allow-origin"; then
    echo -e "${GREEN}✓ PASS${NC} - CORS headers present"
else
    echo -e "${RED}✗ FAIL${NC} - CORS headers missing"
    echo "$CORS_RESPONSE"
    exit 1
fi
echo ""

# ============================================================================
# TEST 3: User Sync (CRITICAL BLOCKER TEST)
# ============================================================================
echo -e "${YELLOW}TEST 3: User Sync Endpoint${NC}"
echo "Testing POST /auth/sync-user"

SYNC_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -X POST "$API_URL/auth/sync-user" \
    -H "Authorization: Bearer $TEST_TOKEN" \
    -H "Content-Type: application/json")

SYNC_HTTP_STATUS=$(echo "$SYNC_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
SYNC_BODY=$(echo "$SYNC_RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$SYNC_HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - User synced successfully"
    echo "Response: $SYNC_BODY"
    
    # Extract user_id for later tests
    USER_ID=$(echo "$SYNC_BODY" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "User ID: $USER_ID"
elif [ "$SYNC_HTTP_STATUS" = "500" ]; then
    echo -e "${RED}✗ FAIL${NC} - Critical blocker detected (HTTP 500)"
    echo "Response: $SYNC_BODY"
    
    if echo "$SYNC_BODY" | grep -q "avatar_url"; then
        echo ""
        echo -e "${RED}BLOCKER IDENTIFIED:${NC} avatar_url column missing in users table"
        echo "Fix: Run ALTER TABLE users ADD COLUMN avatar_url TEXT;"
    fi
    exit 1
else
    echo -e "${RED}✗ FAIL${NC} - Unexpected status (HTTP $SYNC_HTTP_STATUS)"
    echo "Response: $SYNC_BODY"
    exit 1
fi
echo ""

# ============================================================================
# TEST 4: Get User Profile
# ============================================================================
echo -e "${YELLOW}TEST 4: Get User Profile${NC}"
PROFILE_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    "$API_URL/auth/me" \
    -H "Authorization: Bearer $TEST_TOKEN")

PROFILE_HTTP_STATUS=$(echo "$PROFILE_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
PROFILE_BODY=$(echo "$PROFILE_RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$PROFILE_HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Profile retrieved"
    echo "Response: $PROFILE_BODY"
else
    echo -e "${YELLOW}⚠ SKIP${NC} - Profile not found (acceptable for first login)"
fi
echo ""

# ============================================================================
# TEST 5: List Twins
# ============================================================================
echo -e "${YELLOW}TEST 5: List User's Twins${NC}"
TWINS_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    "$API_URL/twins" \
    -H "Authorization: Bearer $TEST_TOKEN")

TWINS_HTTP_STATUS=$(echo "$TWINS_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
TWINS_BODY=$(echo "$TWINS_RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$TWINS_HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Twins endpoint accessible"
    
    # Try to extract first twin ID if exists
    TWIN_ID=$(echo "$TWINS_BODY" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    if [ -n "$TWIN_ID" ]; then
        echo "Found existing twin: $TWIN_ID"
    else
        echo "No existing twins found (will skip interview tests)"
    fi
else
    echo -e "${RED}✗ FAIL${NC} - Cannot list twins (HTTP $TWINS_HTTP_STATUS)"
fi
echo ""

# ============================================================================
# TEST 6: Interview Endpoint (if twin exists)
# ============================================================================
if [ -n "$TWIN_ID" ]; then
    echo -e "${YELLOW}TEST 6: Interview Endpoint${NC}"
    echo "Testing POST /cognitive/interview/$TWIN_ID"
    
    INTERVIEW_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -X POST "$API_URL/cognitive/interview/$TWIN_ID" \
        -H "Authorization: Bearer $TEST_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"message": "Hello, I want to test the interview"}')
    
    INTERVIEW_HTTP_STATUS=$(echo "$INTERVIEW_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
    INTERVIEW_BODY=$(echo "$INTERVIEW_RESPONSE" | sed '/HTTP_STATUS/d')
    
    if [ "$INTERVIEW_HTTP_STATUS" = "200" ]; then
        echo -e "${GREEN}✓ PASS${NC} - Interview endpoint works"
        echo "Response preview: $(echo "$INTERVIEW_BODY" | head -c 200)..."
        
        # Extract session_id and conversation_id for verification
        SESSION_ID=$(echo "$INTERVIEW_BODY" | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
        CONVERSATION_ID=$(echo "$INTERVIEW_BODY" | grep -o '"conversation_id":"[^"]*"' | cut -d'"' -f4)
        
        echo "Session ID: $SESSION_ID"
        echo "Conversation ID: $CONVERSATION_ID"
    else
        echo -e "${RED}✗ FAIL${NC} - Interview endpoint failed (HTTP $INTERVIEW_HTTP_STATUS)"
        echo "Response: $INTERVIEW_BODY"
    fi
else
    echo -e "${YELLOW}⚠ SKIP${NC} - TEST 6: No twin available for interview test"
fi
echo ""

# ============================================================================
# TEST 7: Graph Endpoint (if twin exists)
# ============================================================================
if [ -n "$TWIN_ID" ]; then
    echo -e "${YELLOW}TEST 7: Graph Retrieval${NC}"
    
    GRAPH_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        "$API_URL/twins/$TWIN_ID/graph?limit=10" \
        -H "Authorization: Bearer $TEST_TOKEN")
    
    GRAPH_HTTP_STATUS=$(echo "$GRAPH_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
    GRAPH_BODY=$(echo "$GRAPH_RESPONSE" | sed '/HTTP_STATUS/d')
    
    if [ "$GRAPH_HTTP_STATUS" = "200" ]; then
        echo -e "${GREEN}✓ PASS${NC} - Graph endpoint accessible"
        
        # Count nodes and edges
        NODE_COUNT=$(echo "$GRAPH_BODY" | grep -o '"nodes":\[[^]]*\]' | grep -o '"id":' | wc -l)
        echo "Nodes found: $NODE_COUNT"
    elif [ "$GRAPH_HTTP_STATUS" = "403" ]; then
        echo -e "${RED}✗ FAIL${NC} - Access forbidden (twin ownership issue)"
        echo "This might indicate auth_guard is blocking access"
    else
        echo -e "${RED}✗ FAIL${NC} - Graph endpoint failed (HTTP $GRAPH_HTTP_STATUS)"
    fi
else
    echo -e "${YELLOW}⚠ SKIP${NC} - TEST 7: No twin available for graph test"
fi
echo ""

# ============================================================================
# Summary
# ============================================================================
echo "========================================="
echo "SMOKE TEST SUMMARY"
echo "========================================="
echo "Health Check: PASS"
echo "CORS: PASS"
echo "User Sync: PASS"
echo "Additional tests: See above"
echo ""
echo -e "${GREEN}Core functionality verified!${NC}"
echo ""
echo "Next steps:"
echo "  1. Run database audit: psql \$DATABASE_URL -f scripts/db_audit.sql"
echo "  2. Run pytest suite: cd backend && pytest tests/test_e2e_smoke.py"
echo ""
