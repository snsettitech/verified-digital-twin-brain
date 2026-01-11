-- Database Diagnostic Script
-- Run this in Supabase SQL Editor to identify what's missing

-- ============================================================================
-- 1. CHECK TABLES COUNT
-- ============================================================================
SELECT 
    'Table Count' as check_type,
    COUNT(*)::text as result,
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
SELECT 
    'Critical Tables' as check_type,
    t.table_name as result,
    CASE 
        WHEN it.table_name IS NOT NULL THEN '✅ EXISTS'
        ELSE '❌ MISSING'
    END as status
FROM (VALUES 
    ('users'),
    ('tenants'),
    ('twins'),
    ('conversations'),
    ('messages'),
    ('verified_qna'),
    ('interview_sessions'),
    ('nodes'),
    ('edges'),
    ('access_groups'),
    ('metrics')
) AS t(table_name)
LEFT JOIN information_schema.tables it 
    ON it.table_name = t.table_name 
    AND it.table_schema = 'public'
ORDER BY status, t.table_name;

-- ============================================================================
-- 3. CHECK USERS TABLE STRUCTURE
-- ============================================================================
SELECT 
    'Users Table Columns' as check_type,
    column_name || ' (' || data_type || ')' as result,
    CASE 
        WHEN column_name IN ('id', 'email', 'tenant_id') THEN '✅ REQUIRED'
        ELSE '⚠️ OPTIONAL'
    END as status
FROM information_schema.columns 
WHERE table_name = 'users' 
AND table_schema = 'public'
ORDER BY ordinal_position;

-- ============================================================================
-- 4. CHECK RPC FUNCTIONS
-- ============================================================================
SELECT 
    'RPC Functions' as check_type,
    f.proname as result,
    CASE 
        WHEN p.proname IS NOT NULL THEN '✅ EXISTS'
        ELSE '❌ MISSING'
    END as status
FROM (VALUES 
    ('get_or_create_interview_session'),
    ('get_nodes_system'),
    ('create_node_system'),
    ('get_edges_system'),
    ('create_edge_system')
) AS f(proname)
LEFT JOIN pg_proc p ON p.proname = f.proname
ORDER BY status, f.proname;

-- ============================================================================
-- 5. CHECK RLS STATUS
-- ============================================================================
SELECT 
    'RLS Status' as check_type,
    tablename as result,
    CASE 
        WHEN rowsecurity THEN '✅ ENABLED'
        ELSE '❌ DISABLED'
    END as status
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'twins', 'messages', 'conversations', 'verified_qna')
ORDER BY tablename;

-- ============================================================================
-- 6. SUMMARY REPORT
-- ============================================================================
SELECT 
    'SUMMARY' as check_type,
    'Total Tables: ' || COUNT(*)::text as result,
    CASE 
        WHEN COUNT(*) >= 25 THEN '✅ Database appears complete'
        WHEN COUNT(*) >= 15 THEN '⚠️ Some migrations may be missing'
        ELSE '❌ Critical migrations missing'
    END as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE';

