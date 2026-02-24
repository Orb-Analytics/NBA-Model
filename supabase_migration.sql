-- Migration Script: Update predictions table to match Figma app schema
-- This script migrates from the old schema to the new Figma-compatible schema
-- Run this in your Supabase SQL Editor

-- ============================================================================
-- OPTION 1: Fresh Start (Recommended if you haven't deployed yet)
-- ============================================================================
-- Drop the existing table and recreate with new schema
-- WARNING: This deletes all existing data!

-- DROP TABLE IF EXISTS predictions CASCADE;

-- Then run the full supabase_schema.sql file to recreate with new structure


-- ============================================================================
-- OPTION 2: Migrate Existing Data (If you have production data to preserve)
-- ============================================================================

-- Step 1: Create backup table
CREATE TABLE predictions_backup AS SELECT * FROM predictions;

-- Step 2: Add new columns to existing table
ALTER TABLE predictions
    ADD COLUMN IF NOT EXISTS pick TEXT,
    ADD COLUMN IF NOT EXISTS confidence TEXT,
    ADD COLUMN IF NOT EXISTS home_score INTEGER,
    ADD COLUMN IF NOT EXISTS away_score INTEGER,
    ADD COLUMN IF NOT EXISTS sport TEXT DEFAULT 'NBA',
    ADD COLUMN IF NOT EXISTS game_time TEXT,
    ADD COLUMN IF NOT EXISTS analysis TEXT,
    ADD COLUMN IF NOT EXISTS ml_probability NUMERIC(5,2),
    ADD COLUMN IF NOT EXISTS implied_probability NUMERIC(5,2);

-- Step 3: Migrate data from old columns to new columns
UPDATE predictions
SET 
    -- Create "pick" from pick_team and spread
    pick = CASE 
        WHEN pick_side = 'FAVORITE' THEN pick_team || ' ' || spread::TEXT
        WHEN pick_side = 'UNDERDOG' THEN pick_team || ' +' || ABS(spread)::TEXT
        ELSE pick_team || ' ' || spread::TEXT
    END,
    
    -- Set confidence based on edge
    confidence = CASE 
        WHEN edge >= 8.0 THEN 'high'
        WHEN edge >= 5.0 THEN 'medium'
        ELSE 'low'
    END,
    
    -- Convert result from 'PENDING' to NULL
    result = CASE 
        WHEN result = 'PENDING' THEN NULL
        ELSE result
    END,
    
    -- Rename probability columns
    ml_probability = model_prob,
    implied_probability = implied_prob
WHERE pick IS NULL;  -- Only update records that haven't been migrated yet

-- Step 4: Convert odds from numeric to text
ALTER TABLE predictions ALTER COLUMN odds TYPE TEXT USING 
    CASE 
        WHEN odds < 0 THEN odds::INTEGER::TEXT
        WHEN odds > 0 THEN '+' || odds::INTEGER::TEXT
        ELSE '-110'
    END;

-- Step 5: Change id from BIGSERIAL to UUID (if needed)
-- WARNING: This will regenerate all IDs! Only do this if your app doesn't reference existing IDs
-- ALTER TABLE predictions DROP CONSTRAINT predictions_pkey;
-- ALTER TABLE predictions DROP COLUMN id;
-- ALTER TABLE predictions ADD COLUMN id UUID PRIMARY KEY DEFAULT gen_random_uuid();

-- Step 6: Drop old columns (once you've verified new columns are correct)
-- ALTER TABLE predictions 
--     DROP COLUMN IF EXISTS pick_team,
--     DROP COLUMN IF EXISTS pick_side,
--     DROP COLUMN IF EXISTS model_prob,
--     DROP COLUMN IF EXISTS implied_prob,
--     DROP COLUMN IF EXISTS actual_cover;

-- Step 7: Update indexes
DROP INDEX IF EXISTS idx_predictions_pick_team;
CREATE INDEX IF NOT EXISTS idx_predictions_confidence ON predictions(confidence);


-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Check that migration worked
SELECT 
    date,
    home_team,
    away_team,
    pick,
    spread,
    edge,
    confidence,
    result,
    odds,
    ml_probability,
    implied_probability
FROM predictions
LIMIT 5;

-- Count records by confidence level
SELECT 
    confidence,
    COUNT(*) as count,
    AVG(edge) as avg_edge,
    SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses
FROM predictions
WHERE result IN ('WIN', 'LOSS')
GROUP BY confidence
ORDER BY 
    CASE confidence 
        WHEN 'high' THEN 1 
        WHEN 'medium' THEN 2 
        WHEN 'low' THEN 3 
    END;


-- ============================================================================
-- Rollback (in case something goes wrong)
-- ============================================================================

-- If you created a backup and need to restore:
-- DROP TABLE predictions;
-- ALTER TABLE predictions_backup RENAME TO predictions;
