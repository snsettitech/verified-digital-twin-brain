# Verify RAG: How to Run Retrieval Verification Locally

> Reusable command card for verifying RAG (Retrieval-Augmented Generation) functionality.

## Purpose

Verify that the RAG system retrieves relevant context and generates grounded answers before pushing changes that touch retrieval/answering code.

## Quick Verification

### 1. Prerequisites

**Services Running:**
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Supabase: Connected and accessible
- Pinecone: Connected and accessible

**Test Data:**
- At least one twin created
- At least one document uploaded and ingested
- Verify ingestion completed (check `sources` table status)

### 2. Basic RAG Flow

**Test Chat Endpoint:**
```bash
export TOKEN="<your-jwt-token>"
export TWIN_ID="<your-twin-id>"

curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "twin_id": "'$TWIN_ID'",
    "message": "What is the main topic of the uploaded documents?",
    "conversation_id": null
  }'

# Expected: 200 OK with answer containing:
# - "content": Answer text
# - "citations": Array of source references
# - "confidence_score": Number between 0 and 1
```

**Check Response:**
- Answer should reference uploaded document content
- Citations should include source IDs
- Confidence score should be > 0.5 for relevant queries

### 3. Verify Retrieval

**Check Vector Search:**
1. Query should retrieve chunks from Pinecone
2. Chunks should be filtered by `twin_id`
3. Top-k results should be relevant to query

**Check Verified QnA (if exists):**
1. If verified QnA exists for query, should use it
2. Verified QnA takes priority over vector search
3. Answer should match verified QnA exactly

**Check Citations:**
1. Citations should reference actual sources
2. Source IDs should exist in database
3. Citation URLs should be valid (if configured)

### 4. Common Issues

**Empty or Generic Answers:**
- No documents ingested for this twin
- Retrieval returned no results
- Check Pinecone index has vectors for this `twin_id`
- Verify ingestion completed successfully

**Wrong Context Retrieved:**
- Query not specific enough
- Vector embeddings not matching
- Check if embeddings were generated correctly during ingestion

**Missing Citations:**
- Sources not linked correctly
- Citation extraction logic broken
- Check `citations` array in response

**Low Confidence Scores:**
- Retrieval didn't find relevant context
- Answer is uncertain (may trigger escalation)
- Check retrieval scores in logs

## Detailed Debugging

### Check Database

**Verify Sources:**
```sql
SELECT id, filename, status, twin_id FROM sources 
WHERE twin_id = '<your-twin-id>' AND status = 'completed';
```

**Verify Verified QnA:**
```sql
SELECT id, question, answer, is_active FROM verified_qna 
WHERE twin_id = '<your-twin-id>' AND is_active = true;
```

**Verify Conversations:**
```sql
SELECT id, twin_id, created_at FROM conversations 
WHERE twin_id = '<your-twin-id>' ORDER BY created_at DESC LIMIT 5;
```

### Check Pinecone

**Verify Vectors Exist:**
```python
# In Python shell
from modules.clients import get_pinecone_client
import os

pc = get_pinecone_client()
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

# Query for vectors with twin_id filter
results = index.query(
    vector=[0.0] * 3072,  # Dummy vector
    top_k=10,
    include_metadata=True,
    filter={"twin_id": "<your-twin-id>"}
)
print(f"Found {len(results.matches)} vectors for twin")
```

### Check Logs

**Backend Logs:**
- Look for retrieval scores
- Check for errors in embedding generation
- Verify Pinecone queries succeeded

**Frontend Console:**
- Check for API errors
- Verify chat messages are sent
- Check response structure

## Test Scenarios

### 1. Basic Retrieval
- Query: "What is mentioned about X?"
- Expected: Answer references document content about X
- Citations: Should include source ID

### 2. Verified QnA Priority
- Query: Question that matches verified QnA
- Expected: Answer uses verified QnA exactly
- Citations: Should reference verified QnA

### 3. No Context Found
- Query: "Something completely unrelated"
- Expected: Either "I don't know" response OR escalation triggered
- Confidence: Should be low (< 0.5)

### 4. Multi-Source Retrieval
- Query: Topic mentioned in multiple documents
- Expected: Answer synthesizes multiple sources
- Citations: Should include multiple source IDs

## Reference Documents

- **Retrieval Code**: `backend/modules/retrieval.py`
- **Answering Code**: `backend/modules/answering.py`
- **Verified QnA**: `backend/modules/verified_qna.py`
- **E2E Tests**: `docs/e2e_tests.md`

## Checklist

Before pushing RAG changes:
- [ ] Chat endpoint returns answers with citations
- [ ] Retrieval finds relevant context
- [ ] Citations reference valid sources
- [ ] Verified QnA takes priority when matching
- [ ] Low-confidence queries trigger escalation (if configured)
- [ ] Multi-tenant isolation works (twin_id filtering)
- [ ] No errors in backend logs
- [ ] No errors in frontend console

