-- ============================================================================
-- Database Schema Audit Script
-- Purpose: Verify all required tables, columns, and RPC functions exist
-- Usage: psql $DATABASE_URL -f scripts/db_audit.sql
-- ============================================================================

\echo '==================== DATABASE AUDIT STARTING ===================='
\echo ''

-- Connection Info
\echo 'Connection Info:'
SELECT current_database() AS database, current_user AS user, version() AS postgres_version;
\echo ''

-- ============================================================================
-- CHECK 1: Critical Tables Exist
-- ============================================================================
\echo '==================== CHECK 1: Tables Existence ===================='

DO $$
DECLARE
    tables TEXT[] := ARRAY['users', 'twins', 'tenants', 'interview_sessions', 'nodes', 'edges', 'conversations'];
    tbl TEXT;
    exists BOOLEAN;
BEGIN
    FOREACH tbl IN ARRAY tables
    LOOP
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = tbl
        ) INTO exists;
        
        IF exists THEN
            RAISE NOTICE 'Table: % - EXISTS ✓', tbl;
        ELSE
            RAISE WARNING 'Table: % - MISSING ✗', tbl;
        END IF;
    END LOOP;
END $$;

\echo ''

-- ============================================================================
-- CHECK 2: Users Table Schema (CRITICAL BLOCKER CHECK)
-- ============================================================================
\echo '==================== CHECK 2: Users Table Columns ===================='

SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
  AND table_name = 'users'
ORDER BY ordinal_position;

\echo ''
\echo 'CRITICAL: Verify avatar_url column exists above ↑'
\echo ''

-- ============================================================================
-- CHECK 3: Interview Sessions Table Schema
-- ============================================================================
\echo '==================== CHECK 3: Interview Sessions Table Columns ===================='

SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
  AND table_name = 'interview_sessions'
ORDER BY ordinal_position;

\echo ''

-- ============================================================================
-- CHECK 4: Nodes and Edges Schema
-- ============================================================================
\echo '==================== CHECK 4: Nodes Table Columns ===================='

SELECT 
    column_name,
    data_type
FROM information_schema.columns 
WHERE table_schema = 'public' 
  AND table_name = 'nodes'
ORDER BY ordinal_position;

\echo ''
\echo '==================== CHECK 5: Edges Table Columns ===================='

SELECT 
    column_name,
    data_type
FROM information_schema.columns 
WHERE table_schema = 'public' 
  AND table_name = 'edges'
ORDER BY ordinal_position;

\echo ''

-- ============================================================================
-- CHECK 6: RPC Functions Exist
-- ============================================================================
\echo '==================== CHECK 6: RPC Functions ===================='

SELECT 
    proname AS function_name,
    pronargs AS num_args,
    prorettype::regtype AS return_type
FROM pg_proc 
WHERE proname IN (
    'get_or_create_interview_session',
    'update_interview_session',
    'get_nodes_system',
    'get_edges_system',
    'create_node_system',
    'create_edge_system',
    'check_twin_tenant_access',
    'get_twin_system'
)
ORDER BY proname;

\echo ''
\echo 'Expected: 8 functions listed above'
\echo ''

-- ============================================================================
-- CHECK 7: Indexes (Performance Check)
-- ============================================================================
\echo '==================== CHECK 7: Key Indexes ===================='

SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('users', 'twins', 'interview_sessions', 'nodes', 'edges')
ORDER BY tablename, indexname;

\echo ''

-- ============================================================================
-- CHECK 8: Row Counts (Data Sanity Check)
-- ============================================================================
\echo '==================== CHECK 8: Table Row Counts ===================='

DO $$
DECLARE
    cnt INTEGER;
BEGIN
    SELECT COUNT(*) INTO cnt FROM users;
    RAISE NOTICE 'users: % rows', cnt;
    
    SELECT COUNT(*) INTO cnt FROM twins;
    RAISE NOTICE 'twins: % rows', cnt;
    
    SELECT COUNT(*) INTO cnt FROM interview_sessions;
    RAISE NOTICE 'interview_sessions: % rows', cnt;
    
    SELECT COUNT(*) INTO cnt FROM nodes;
    RAISE NOTICE 'nodes: % rows', cnt;
    
    SELECT COUNT(*) INTO cnt FROM edges;
    RAISE NOTICE 'edges: % rows', cnt;
END $$;

\echo ''
\echo '==================== DATABASE AUDIT COMPLETE ===================='
\echo ''
\echo 'CRITICAL CHECKS:'
\echo '  1. avatar_url column in users table'
\echo '  2. interview_sessions table exists'
\echo '  3. All 8 RPC functions present'
\echo ''
\echo 'If any checks failed, refer to VERIFICATION_PLAN.md for fixes'
\echo ''
