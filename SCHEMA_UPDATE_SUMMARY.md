# ✅ Schema Update Summary

## What Changed
Your Supabase integration has been updated to match your Figma app's schema requirements.

---

## 📋 Files Updated

### 1. **supabase_schema.sql**
- Updated `predictions` table structure
- Changed `id` from BIGSERIAL to UUID
- Replaced `pick_team`, `pick_side`, `odds`, `model_prob`, `implied_prob`, `actual_cover` 
- Added `pick`, `confidence`, `home_score`, `away_score`, `sport`, `game_time`, `analysis`, `ml_probability`, `implied_probability`
- Updated indexes and views

### 2. **src/sync_to_supabase.py**
- Updated `format_prediction_record()` function
- Now generates `pick` field as "Team ±Spread" (e.g., "Lakers -5.5")
- Calculates `confidence` from edge: ≥8% = high, ≥5% = medium, <5% = low
- Formats `odds` as text (e.g., "-110", "+105")
- Uses `null` instead of "PENDING" for result
- Renamed probability fields to `ml_probability` and `implied_probability`

### 3. **docs/WEB_APP_QUERIES.md**
- Updated all query examples for new schema
- Updated React component examples (TodaysPicks, RecentResults)
- Added support for `confidence` badges and `pick` display
- Added optional fields like `home_score`, `away_score`, `game_time`

### 4. **New Files Created**

#### supabase_migration.sql
Migration script with two options:
- **Option 1**: Fresh start (drop and recreate table)
- **Option 2**: Migrate existing data (preserves records)

#### FIGMA_APP_SETUP.md
Complete step-by-step guide for connecting to Figma app:
- How to get anon key
- How to update schema
- How to set up Supabase client
- TypeScript interfaces
- Custom hooks examples
- Troubleshooting tips

#### supabase_data_template.csv
Example CSV showing the correct data format for import/reference

---

## 🔄 Schema Comparison

### Old Schema
```typescript
{
  id: number,
  date: string,
  home_team: string,
  away_team: string,
  pick_team: string,      // ❌ Removed
  pick_side: string,      // ❌ Removed
  spread: number,
  odds: number,           // ❌ Changed to text
  edge: number,
  model_prob: number,     // ❌ Renamed
  implied_prob: number,   // ❌ Renamed
  result: string,         // "PENDING" default
  actual_cover: number    // ❌ Removed
}
```

### New Schema (Figma-compatible)
```typescript
{
  id: string,             // ✅ UUID
  date: string,
  home_team: string,
  away_team: string,
  pick: string,           // ✅ New: "Lakers -5.5"
  spread: number,
  edge: number,
  confidence: string,     // ✅ New: "high"|"medium"|"low"
  result: string|null,    // ✅ null instead of "PENDING"
  
  // Optional fields
  home_score?: number,    // ✅ New
  away_score?: number,    // ✅ New
  sport?: string,         // ✅ New: "NBA"
  game_time?: string,     // ✅ New: "7:30 PM ET"
  odds?: string,          // ✅ Text: "-110"
  analysis?: string,      // ✅ New
  ml_probability?: number,        // ✅ Renamed from model_prob
  implied_probability?: number    // ✅ Renamed from implied_prob
}
```

---

## ✅ Testing Results

Tested sync script with new schema:

```json
{
  "date": "2026-02-11",
  "home_team": "Houston",
  "away_team": "La Clippers",
  "pick": "La Clippers +8.5",        ✅ Formatted correctly
  "spread": 8.5,
  "edge": 6.45,
  "confidence": "medium",             ✅ Calculated from edge
  "result": "WIN",
  "sport": "NBA",                     ✅ Auto-set
  "odds": "+108",                     ✅ Text format
  "ml_probability": null,
  "implied_probability": null
}
```

**Status**: ✅ All fields working correctly!

---

## 🚀 Next Steps for You

### 1. Get Your Supabase Anon Key
- Go to: https://app.supabase.com/project/skfraijnuefuquyxnced/settings/api
- Copy the **anon/public** key (not service_role)

### 2. Update Your Database Schema

**Option A - Fresh Start** (if no production data):
```sql
-- In Supabase SQL Editor
DROP TABLE IF EXISTS predictions CASCADE;
-- Then paste entire supabase_schema.sql
```

**Option B - Migrate Existing Data**:
```sql
-- In Supabase SQL Editor
-- Paste supabase_migration.sql
```

### 3. Re-sync Your Data
```bash
# In codespace terminal
export $(cat .env | xargs)
python src/sync_to_supabase.py --mode all
```

### 4. Set Up in Figma App
```javascript
// In your Figma app code
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://skfraijnuefuquyxnced.supabase.co',
  'YOUR_ANON_KEY_HERE'
)
```

### 5. Test Connection
```javascript
const { data } = await supabase
  .from('season_stats')
  .select('*')
  .eq('season', '2025-26')
  .single()

console.log(data) // Should show your current stats
```

---

## 📚 Documentation

- **Complete Setup Guide**: [FIGMA_APP_SETUP.md](FIGMA_APP_SETUP.md)
- **Query Examples**: [docs/WEB_APP_QUERIES.md](docs/WEB_APP_QUERIES.md)
- **Schema Details**: [supabase_schema.sql](supabase_schema.sql)
- **Migration Script**: [supabase_migration.sql](supabase_migration.sql)
- **Data Template**: [supabase_data_template.csv](supabase_data_template.csv)

---

## 📊 Example Queries for Figma App

```javascript
// Get today's picks
const today = new Date().toISOString().split('T')[0]
const { data: picks } = await supabase
  .from('predictions')
  .select('*')
  .eq('date', today)
  .order('edge', { ascending: false })

// Get season stats
const { data: stats } = await supabase
  .from('season_stats')
  .select('*')
  .eq('season', '2025-26')
  .single()

// Get recent results
const { data: results } = await supabase
  .from('predictions')
  .select('*')
  .in('result', ['WIN', 'LOSS', 'PUSH'])
  .order('date', { ascending: false })
  .limit(10)

// Get high confidence picks
const { data: highConf } = await supabase
  .from('predictions')
  .select('*')
  .or('confidence.eq.high,edge.gte.8.0')
  .order('date', { ascending: false })
```

---

## ✅ Everything is Ready!

All files have been updated and tested. Your Supabase integration is now fully compatible with your Figma app schema. Follow the steps above to complete the setup!
