-- ============================================================================
-- Graph Schema Migration Script
-- Purpose: Fix missing columns that prevent graph edges from being created
-- Usage: Run this in Supabase SQL Editor (Dashboard → SQL Editor → New Query)
-- ============================================================================

-- ============================================================================
-- PART 1: Add missing columns to edges table
-- ============================================================================

-- Add 'properties' column to edges table (stores relationship metadata)
ALTER TABLE edges ADD COLUMN IF NOT EXISTS properties JSONB DEFAULT '{}';

-- Add any other potentially missing columns
ALTER TABLE edges ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE edges ADD COLUMN IF NOT EXISTS weight FLOAT DEFAULT 1.0;

-- ============================================================================
-- PART 2: Add missing columns to nodes table
-- ============================================================================

ALTER TABLE nodes ADD COLUMN IF NOT EXISTS properties JSONB DEFAULT '{}';
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- ============================================================================
-- PART 3: Fix or Create the create_edge_system RPC function
-- ============================================================================

-- Drop existing function if it has wrong signature
DROP FUNCTION IF EXISTS create_edge_system(uuid, uuid, uuid, text, text, jsonb);

-- Create the correct function
CREATE OR REPLACE FUNCTION create_edge_system(
    t_id UUID,
    from_id UUID,
    to_id UUID,
    e_type TEXT,
    e_desc TEXT DEFAULT NULL,
    e_props JSONB DEFAULT '{}'
)
RETURNS TABLE (
    id UUID,
    twin_id UUID,
    source_id UUID,
    target_id UUID,
    type TEXT,
    description TEXT,
    properties JSONB,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    INSERT INTO edges (twin_id, source_id, target_id, type, description, properties)
    VALUES (t_id, from_id, to_id, e_type, e_desc, e_props)
    RETURNING 
        edges.id,
        edges.twin_id,
        edges.source_id,
        edges.target_id,
        edges.type,
        edges.description,
        edges.properties,
        edges.created_at;
END;
$$;

-- ============================================================================
-- PART 4: Fix or Create the create_node_system RPC function
-- ============================================================================

DROP FUNCTION IF EXISTS create_node_system(uuid, text, text, text, jsonb);

CREATE OR REPLACE FUNCTION create_node_system(
    t_id UUID,
    n_name TEXT,
    n_type TEXT,
    n_desc TEXT DEFAULT NULL,
    n_props JSONB DEFAULT '{}'
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    type TEXT,
    description TEXT,
    properties JSONB,
    twin_id UUID,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    node_record RECORD;
BEGIN
    -- Try to find existing node by name and type
    SELECT * INTO node_record 
    FROM nodes 
    WHERE nodes.twin_id = t_id 
      AND nodes.name = n_name 
      AND nodes.type = n_type
    LIMIT 1;
    
    IF FOUND THEN
        -- Update existing node
        RETURN QUERY
        UPDATE nodes 
        SET 
            description = COALESCE(n_desc, nodes.description),
            properties = nodes.properties || n_props,
            updated_at = NOW()
        WHERE nodes.id = node_record.id
        RETURNING 
            nodes.id,
            nodes.name,
            nodes.type,
            nodes.description,
            nodes.properties,
            nodes.twin_id,
            nodes.created_at;
    ELSE
        -- Create new node
        RETURN QUERY
        INSERT INTO nodes (twin_id, name, type, description, properties)
        VALUES (t_id, n_name, n_type, n_desc, n_props)
        RETURNING 
            nodes.id,
            nodes.name,
            nodes.type,
            nodes.description,
            nodes.properties,
            nodes.twin_id,
            nodes.created_at;
    END IF;
END;
$$;

-- ============================================================================
-- PART 5: Fix get_edges_system RPC to include properties
-- ============================================================================

DROP FUNCTION IF EXISTS get_edges_system(uuid, integer);

CREATE OR REPLACE FUNCTION get_edges_system(
    t_id UUID,
    limit_val INTEGER DEFAULT 100
)
RETURNS TABLE (
    id UUID,
    source_id UUID,
    target_id UUID,
    type TEXT,
    description TEXT,
    properties JSONB,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.source_id,
        e.target_id,
        e.type,
        e.description,
        e.properties,
        e.created_at
    FROM edges e
    WHERE e.twin_id = t_id
    ORDER BY e.created_at DESC
    LIMIT limit_val;
END;
$$;

-- ============================================================================
-- PART 6: Fix get_nodes_system RPC to include properties
-- ============================================================================

DROP FUNCTION IF EXISTS get_nodes_system(uuid, integer);

CREATE OR REPLACE FUNCTION get_nodes_system(
    t_id UUID,
    limit_val INTEGER DEFAULT 100
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    type TEXT,
    description TEXT,
    properties JSONB,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        n.id,
        n.name,
        n.type,
        n.description,
        n.properties,
        n.created_at
    FROM nodes n
    WHERE n.twin_id = t_id
    ORDER BY n.created_at DESC
    LIMIT limit_val;
END;
$$;

-- ============================================================================
-- VERIFICATION: Check everything was created correctly
-- ============================================================================

-- Check edges table has properties column
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'edges' AND column_name = 'properties';

-- Check nodes table has properties column  
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'nodes' AND column_name = 'properties';

-- Check RPC functions exist
SELECT proname AS function_name
FROM pg_proc 
WHERE proname IN ('create_edge_system', 'create_node_system', 'get_edges_system', 'get_nodes_system')
ORDER BY proname;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================
SELECT '✅ Graph schema migration complete!' AS result;
