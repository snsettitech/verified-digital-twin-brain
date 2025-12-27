# E2E Test Checklist

> End-to-end test scenarios for the Digital Brain MVP.

## Test Infrastructure

### Tools
- **Playwright**: Browser automation for frontend tests
- **pytest**: Backend API tests
- **Supabase local**: Local database for isolation

### Test Data
- **Tenant A**: Primary test tenant
- **Tenant B**: Secondary tenant for isolation tests
- **User A1, A2**: Users in Tenant A
- **User B1**: User in Tenant B

---

## Critical User Flows

### 1. Sign Up & Onboarding

#### 1.1 New User Sign Up
```
GIVEN a new user visits the site
WHEN they click "Sign Up"
AND enter email and password
AND click submit
THEN they should see the dashboard
AND a tenant record should be created
AND they should see empty state
```

**Steps**:
1. Navigate to `/signup`
2. Fill email: `test-{uuid}@example.com`
3. Fill password: `SecurePass123!`
4. Click submit
5. Wait for redirect to `/dashboard`
6. Verify empty state shows
7. Verify DB has tenant and user records

#### 1.2 Sign In Existing User
```
GIVEN an existing user
WHEN they sign in
THEN they should see their dashboard with their twins
```

#### 1.3 Protected Route Redirect
```
GIVEN an unauthenticated user
WHEN they visit /dashboard
THEN they should be redirected to /login
```

---

### 2. Twin Creation & Configuration

#### 2.1 Create First Twin
```
GIVEN a signed-in user with no twins
WHEN they click "Create Twin"
AND fill in name and select specialization
AND click submit
THEN they should be redirected to onboarding
AND the twin should appear in dashboard
```

**Steps**:
1. Click "Create your first twin" button
2. Fill name: "My VC Brain"
3. Select specialization: "VC Brain"
4. Click "Create"
5. Wait for redirect to `/twins/{id}/onboarding`
6. Navigate to `/dashboard`
7. Verify twin card shows

#### 2.2 Complete Onboarding via Interview
```
GIVEN a twin in pending onboarding
WHEN user completes interview mode
THEN onboarding_status should be 'complete'
AND memory candidates should be created
```

**Steps**:
1. Navigate to `/twins/{id}/onboarding`
2. Respond to 3 interview questions
3. Click "Complete Onboarding"
4. Verify status changes to "complete"
5. Check memory_candidates table has entries

#### 2.3 Complete Onboarding via Upload
```
GIVEN a twin in pending onboarding
WHEN user uploads a document
THEN document should be processed
AND vectors should be in Pinecone
```

---

### 3. Chat Interaction

#### 3.1 Basic Chat
```
GIVEN a twin with some knowledge
WHEN user sends a message
THEN they should receive a response
AND the conversation should be saved
```

**Steps**:
1. Navigate to `/twins/{id}/chat`
2. Type: "Hello, what can you help me with?"
3. Click send
4. Wait for response
5. Verify response appears
6. Verify conversation exists in DB

#### 3.2 Chat Uses Document Context
```
GIVEN a twin with uploaded documents
WHEN user asks about document content
THEN response should reference document info
AND sources should be provided
```

**Steps**:
1. Upload test document with known content
2. Wait for processing complete
3. Ask: "What does the document say about X?"
4. Verify response mentions X
5. Verify sources panel shows document

#### 3.3 Chat Uses Graph Context
```
GIVEN a twin with approved memories
WHEN user asks about known entity
THEN response should include entity info
```

**Steps**:
1. Approve memory candidate for "Acme Corp"
2. Ask: "What do you know about Acme Corp?"
3. Verify response includes Acme Corp info

---

### 4. Memory Learning

#### 4.1 Memory Extraction from Chat
```
GIVEN a chat conversation
WHEN user provides new information
THEN memory candidates should be created
```

**Steps**:
1. Chat: "I usually invest in Series A B2B SaaS"
2. Check memory_candidates table
3. Verify entry for "B2B SaaS" preference

#### 4.2 Memory Approval Flow
```
GIVEN pending memory candidates
WHEN owner approves a candidate
THEN a graph node should be created
AND the memory should affect future chats
```

**Steps**:
1. Navigate to `/twins/{id}/memory`
2. Find pending candidate
3. Click "Approve"
4. Verify graph_nodes entry created
5. Verify candidate status is "approved"

#### 4.3 Memory Rejection Flow
```
GIVEN pending memory candidates
WHEN owner rejects a candidate
THEN no graph node should be created
AND the candidate should be archived
```

---

### 5. Escalation Loop

#### 5.1 Low Confidence Creates Escalation
```
GIVEN a twin with limited knowledge
WHEN user asks unknown question
THEN response should indicate uncertainty
AND escalation should be created
```

**Steps**:
1. Ask: "What's John's favorite restaurant?"
2. Verify response contains uncertainty language
3. Check escalations table for new entry
4. Verify question matches user query

#### 5.2 Owner Responds to Escalation
```
GIVEN a pending escalation
WHEN owner provides response
THEN escalation status should update
```

**Steps**:
1. Navigate to `/twins/{id}/escalations`
2. Find pending escalation
3. Enter response: "John prefers Italian restaurants"
4. Check "Add to brain"
5. Click "Submit"
6. Verify escalation status is "responded"

#### 5.3 Escalation Response Improves Chat
```
GIVEN an escalation was answered with add_to_brain
WHEN user asks the same question again
THEN response should include the owner's answer
AND confidence should be higher
```

**Steps**:
1. After responding to escalation
2. Ask same question: "What's John's favorite restaurant?"
3. Verify response mentions "Italian"
4. Verify confidence > 0.7

---

### 6. Tenant Isolation

#### 6.1 Cross-Tenant Data Isolation - API
```
GIVEN User A creates a twin
WHEN User B requests that twin
THEN User B should get 404
```

**Steps**:
1. As User A: Create twin, get ID
2. As User B: GET `/api/twins/{id}`
3. Verify 404 response

#### 6.2 Cross-Tenant Data Isolation - UI
```
GIVEN User A has twins
WHEN User B views dashboard
THEN User B should not see User A's twins
```

#### 6.3 Cross-Tenant Vector Isolation
```
GIVEN User A uploads document to twin
WHEN User B queries Pinecone
THEN User B should not find User A's vectors
```

**Steps**:
1. As User A: Upload document, get vector IDs
2. As User B: Query Pinecone with same query
3. Verify no results in User B's namespace

---

### 7. Brain Learned Today

#### 7.1 Daily Digest Shows Learnings
```
GIVEN memories were approved today
WHEN user views digest
THEN they should see today's learnings
```

**Steps**:
1. Approve several memory candidates
2. Navigate to dashboard
3. See "Brain learned today" section
4. Verify count matches approved memories
5. Verify highlights are meaningful

---

## Test Matrix

| Test | Priority | Automated | Status |
|------|----------|-----------|--------|
| 1.1 Sign Up | P0 | Yes | Not Started |
| 1.2 Sign In | P0 | Yes | Not Started |
| 1.3 Protected Route | P0 | Yes | Not Started |
| 2.1 Create Twin | P0 | Yes | Not Started |
| 2.2 Interview Onboarding | P0 | Yes | Not Started |
| 2.3 Upload Onboarding | P0 | Yes | Not Started |
| 3.1 Basic Chat | P0 | Yes | Not Started |
| 3.2 Document Context | P0 | Yes | Not Started |
| 3.3 Graph Context | P0 | Yes | Not Started |
| 4.1 Memory Extraction | P0 | Yes | Not Started |
| 4.2 Memory Approval | P0 | Yes | Not Started |
| 4.3 Memory Rejection | P1 | Yes | Not Started |
| 5.1 Escalation Creation | P0 | Yes | Not Started |
| 5.2 Escalation Response | P0 | Yes | Not Started |
| 5.3 Escalation Learning | P0 | Yes | Not Started |
| 6.1 API Isolation | P0 | Yes | Not Started |
| 6.2 UI Isolation | P0 | Yes | Not Started |
| 6.3 Vector Isolation | P0 | Yes | Not Started |
| 7.1 Daily Digest | P1 | Yes | Not Started |

---

## Running Tests

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm run test:e2e
```

### Security Tests
```bash
cd backend
pytest tests/test_security.py -v
```

### Full E2E Suite
```bash
# Start local services
docker-compose up -d

# Run all tests
./scripts/run_e2e.sh
```
