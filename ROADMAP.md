# Roadmap: Verified Digital Twin Brain

This roadmap outlines the evolution of the Verified Digital Twin Brain platform, moving from a grounded Q&A engine to a fully autonomous, accountable agent.

## Current Progress: Phase 1 (MVP) - Grounded Answers
**Status: Completed**

- [x] Multi-tenant database schema (Supabase).
- [x] Document ingestion pipeline (PDF extraction -> Chunking -> OpenAI Embeddings -> Pinecone).
- [x] RAG-based chat API with citation support.
- [x] Confidence-based escalation logic.
- [x] Basic Next.js dashboard and chat interface.

---

## Next Milestone: Phase 2 - Trust & Verified Memory
**Status: Pending**

The goal is to move from "AI answering" to "Owner verified" knowledge.

- [ ] **Owner Escalation Inbox**: UI for owners to view and resolve low-confidence questions.
- [ ] **Verified Memory Injection**: Automated process to turn owner's manual responses into high-priority vector embeddings.
- [ ] **Enhanced Provenance**: Detailed UI showing exact document snippets used for answers.
- [ ] **Twin Personalization**: System instructions and "Voice" configuration for different twins.

---

## Future Milestone: Phase 3 - Assisted Work & Tool Integration
**Status: Planned**

Moving from answering questions to assisting with tasks with human-in-the-loop approvals.

- [ ] **Drafting Workflows**: AI drafts emails, summaries, and documents for owner approval.
- [ ] **Tool Connections**: Integration with Gmail, Slack, and Google Calendar.
- [ ] **Approval Gates**: Every proposed action requires a "thumbs up" from the owner before execution.

---

## Long-term Vision: Phase 4 - Autonomous Accountability
**Status: Research**

Full delegation within scoped permissions and rigorous audit trails.

- [ ] **Policy Enforcement**: Define granular rules for what the twin can and cannot do autonomously.
- [ ] **Multi-step Workflows**: Handling complex requests that require multiple tool interactions.
- [ ] **Full Auditability**: Immutable log of every decision, source used, and action taken by the twin.

