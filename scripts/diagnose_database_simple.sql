-- Database Diagnostic Script (Simplified)
-- Run this in Supabase SQL Editor to identify what's missing

-- ============================================================================
-- 1. CHECK TABLES COUNT
-- ============================================================================
SELECT 
    COUNT(*) as table_count,
    CASE 
        WHEN COUNT(*) >= 25 THEN '✅ GOOD (25-30 expected)'
        ELSE '❌ TOO FEW - Migrations likely incomplete'
    END as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE';

-- ============================================================================
-- 2. CHECK CRITICAL TABLES EXIST
-- ============================================================================
WITH required_tables AS (
    SELECT unnest(ARRAY[
        'users', 'tenants', 'twins', 'conversations', 'messages',
        'verified_qna', 'interview_sessions', 'nodes', 'edges',
        'access_groups', 'metrics'
    ]) AS table_name
)
SELECT 
    rt.table_name,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = rt.table_name
        ) THEN '✅ EXISTS'
        ELSE '❌ MISSING'
    END as status
FROM required_tables rt
ORDER BY status, rt.table_name;

-- ============================================================================
-- 3. CHECK USERS TABLE STRUCTURE
-- ============================================================================
SELECT 
    column_name,
    data_type,
    CASE 
        WHEN column_name IN ('id', 'email', 'tenant_id') THEN '✅ REQUIRED'
        ELSE '⚠️ OPTIONAL'
    END as importance
FROM information_schema.columns 
WHERE table_name = 'users' 
AND table_schema = 'public'
ORDER BY ordinal_position;

-- ============================================================================
-- 4. CHECK RPC FUNCTIONS
-- ============================================================================
WITH required_functions AS (
    SELECT unnest(ARRAY[
        'get_or_create_interview_session',
        'get_nodes_system',
        'create_node_system',
        'get_edges_system',
        'create_edge_system'
    ]) AS function_name
)
SELECT 
    rf.function_name,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM pg_proc 
            WHERE proname = rf.function_name
        ) THEN '✅ EXISTS'
        ELSE '❌ MISSING'
    END as status
FROM required_functions rf
ORDER BY status, rf.function_name;

-- ============================================================================
-- 5. CHECK RLS STATUS
-- ============================================================================
SELECT 
    tablename,
    CASE 
        WHEN rowsecurity THEN '✅ ENABLED'
        ELSE '❌ DISABLED'
    END as rls_status
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'twins', 'messages', 'conversations', 'verified_qna')
ORDER BY tablename;

