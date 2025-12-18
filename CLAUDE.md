# CLAUDE.md

This file provides guidance to Claude Code and Cursor when working with the **Verified Digital Twin Brain** repository.

## Workspace Overview

This project consists of a FastAPI backend and a Next.js frontend, integrated with Supabase (Postgres/Auth), Pinecone (Vector DB), and OpenAI (LLMs).

## Common Commands

### Backend (FastAPI)
Navigate to project: `cd backend`

**Setup:**
```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Development:**
```bash
# Run the FastAPI server
python main.py
# OR
uvicorn main:app --reload
```

**Testing:**
```bash
python test_system.py
```

### Frontend (Next.js)
Navigate to project: `cd frontend`

**Development:**
```bash
npm install
npm run dev
```

## Architecture & Project Structure

- `backend/`: FastAPI application.
  - `main.py`: Application entry point.
  - `modules/`: Core logic modules (ingestion, retrieval, answering, escalation).
  - `modules/clients.py`: Centralized client initialization for OpenAI and Pinecone.
- `frontend/`: Next.js 14 application using Tailwind CSS.
- `supabase_schema.sql`: Database schema for Supabase.

## Guidelines

- **Style**: Follow PEP 8 for Python and standard React/Next.js conventions for TypeScript.
- **RAG Integrity**: Ensure all answers include citations from the knowledge base.
- **Trust Layer**: High importance on confidence scoring and escalation for low-confidence answers.
- **Security**: Never commit `.env` files. Use `.env.example` for template keys.

