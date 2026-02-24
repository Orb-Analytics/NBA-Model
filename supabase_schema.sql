-- Supabase Database Schema for NBA Prediction Model Web App
-- Run this in your Supabase SQL Editor to create the tables

-- ============================================================================
-- Table: predictions
-- Stores all predictions (both pending and completed with results)
-- Schema matches Figma app requirements
-- ============================================================================

CREATE TABLE IF NOT EXISTS predictions (
    -- Required columns
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    pick TEXT NOT NULL,  -- e.g., "Lakers -5.5" or "Warriors +5.5"
    spread NUMERIC(4,1) NOT NULL,
    edge NUMERIC(5,2) NOT NULL,
    confidence TEXT,  -- 'high', 'medium', 'low' or numeric value
    result TEXT,  -- 'WIN', 'LOSS', 'PUSH', or NULL for pending
    
    -- Optional but recommended columns
    home_score INTEGER,
    away_score INTEGER,
    sport TEXT DEFAULT 'NBA',
    game_time TEXT,
    odds TEXT DEFAULT '-110',
    analysis TEXT,
    ml_probability NUMERIC(5,2),  -- Model probability (0-100)
    implied_probability NUMERIC(5,2),  -- Implied probability from odds (0-100)
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint to prevent duplicate predictions
    UNIQUE(date, home_team, away_team)
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(date DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_result ON predictions(result);
CREATE INDEX IF NOT EXISTS idx_predictions_confidence ON predictions(confidence);

-- Add comment
COMMENT ON TABLE predictions IS 'NBA game predictions with results';


-- ============================================================================
-- Table: season_stats
-- Stores overall season performance statistics
-- ============================================================================

CREATE TABLE IF NOT EXISTS season_stats (
    id BIGSERIAL PRIMARY KEY,
    season TEXT NOT NULL UNIQUE,
    wins INTEGER NOT NULL DEFAULT 0,
    losses INTEGER NOT NULL DEFAULT 0,
    total_games INTEGER NOT NULL DEFAULT 0,
    win_percentage NUMERIC(5,2) NOT NULL DEFAULT 0,
    units NUMERIC(8,2) NOT NULL DEFAULT 0,
    roi NUMERIC(6,2) NOT NULL DEFAULT 0,
    start_date DATE,
    end_date DATE,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add comment
COMMENT ON TABLE season_stats IS 'Season performance statistics';


-- ============================================================================
-- Function: Update timestamp on row update
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add trigger to predictions table
DROP TRIGGER IF EXISTS update_predictions_updated_at ON predictions;
CREATE TRIGGER update_predictions_updated_at
    BEFORE UPDATE ON predictions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================================
-- Row Level Security (RLS) Policies
-- Enable RLS and set policies for public read access
-- ============================================================================

-- Enable RLS on tables
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE season_stats ENABLE ROW LEVEL SECURITY;

-- Allow public read access (for web app)
CREATE POLICY "Allow public read access on predictions"
    ON predictions FOR SELECT
    USING (true);

CREATE POLICY "Allow public read access on season_stats"
    ON season_stats FOR SELECT
    USING (true);

-- Allow authenticated insert/update (for API sync)
CREATE POLICY "Allow authenticated insert on predictions"
    ON predictions FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated update on predictions"
    ON predictions FOR UPDATE
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated insert on season_stats"
    ON season_stats FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated update on season_stats"
    ON season_stats FOR UPDATE
    TO authenticated
    USING (true);


-- ============================================================================
-- Helpful Views for Web App
-- ============================================================================

-- View: Today's picks
CREATE OR REPLACE VIEW todays_picks AS
SELECT 
    *
FROM predictions
WHERE date = CURRENT_DATE
ORDER BY edge DESC;

-- View: Recent results (last 10 games)
CREATE OR REPLACE VIEW recent_results AS
SELECT 
    *
FROM predictions
WHERE result IN ('WIN', 'LOSS', 'PUSH')
ORDER BY date DESC
LIMIT 10;

-- View: High confidence picks (edge >= 5% or confidence = 'high')
CREATE OR REPLACE VIEW high_confidence_picks AS
SELECT 
    *
FROM predictions
WHERE edge >= 5.0 OR confidence = 'high'
ORDER BY date DESC, edge DESC;


-- ============================================================================
-- Sample Queries for Web App
-- ============================================================================

-- Get today's picks
-- SELECT * FROM todays_picks;

-- Get last 7 days of results
-- SELECT * FROM predictions 
-- WHERE date >= CURRENT_DATE - INTERVAL '7 days'
-- ORDER BY date DESC;

-- Get season stats
-- SELECT * FROM season_stats WHERE season = '2025-26';

-- Get picks by team (home or away)
-- SELECT * FROM predictions 
-- WHERE home_team = 'Lakers' OR away_team = 'Lakers'
-- ORDER BY date DESC;

-- Get high confidence picks only
-- SELECT * FROM predictions 
-- WHERE confidence = 'high' OR edge >= 8.0
-- ORDER BY date DESC;

-- Get win/loss breakdown by date
-- SELECT 
--     date,
--     COUNT(*) as total_picks,
--     SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
--     SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
--     SUM(CASE WHEN result = 'PUSH' THEN 1 ELSE 0 END) as pushes
-- FROM predictions
-- WHERE result IN ('WIN', 'LOSS', 'PUSH')
-- GROUP BY date
-- ORDER BY date DESC;
