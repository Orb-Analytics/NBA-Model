# 🎨 Figma Web App Supabase Integration Guide

## Overview
This guide walks you through connecting your NBA prediction data in Supabase to your Figma web app.

---

## ✅ What's Been Updated

Your Supabase integration has been updated to match your Figma app's requirements:

### Schema Changes
- **New `pick` column**: Displays as "Lakers -5.5" or "Warriors +5.5" (single field)
- **New `confidence` field**: "high", "medium", or "low" (calculated from edge %)
- **Result values**: "WIN", "LOSS", "PUSH", or `null` for pending
- **Probability fields**: Renamed to `ml_probability` and `implied_probability`
- **Optional fields**: Added `home_score`, `away_score`, `sport`, `game_time`, `analysis`

### Files Updated
✅ `supabase_schema.sql` - Updated table structure  
✅ `src/sync_to_supabase.py` - Updated data formatting  
✅ `docs/WEB_APP_QUERIES.md` - Updated query examples  
✅ `supabase_migration.sql` - Migration script for existing data (if needed)

---

## 🚀 Step-by-Step Setup

### Step 1: Get Your Supabase Anon Key

1. Go to your Supabase project: https://app.supabase.com/project/skfraijnuefuquyxnced
2. Navigate to **Settings** → **API**
3. Copy the **anon/public** key (NOT the service_role key)
4. This key is safe to use in your frontend code

### Step 2: Update Your Supabase Schema

Choose one of these options:

#### Option A: Fresh Start (if you haven't deployed yet)
```sql
-- In Supabase SQL Editor
DROP TABLE IF EXISTS predictions CASCADE;

-- Then paste the contents of supabase_schema.sql
```

#### Option B: Migrate Existing Data (if you have production data)
```sql
-- In Supabase SQL Editor
-- Paste the contents of supabase_migration.sql

-- This will:
-- 1. Create backup of existing data
-- 2. Add new columns (pick, confidence, etc.)
-- 3. Migrate data from old format to new format
-- 4. Preserve all existing records
```

### Step 3: Re-sync Your Data

After updating the schema, re-sync your data with the updated format:

```bash
# In your codespace terminal
export $(cat .env | xargs)
python src/sync_to_supabase.py --mode all
```

This will populate your database with all historical data in the new format.

### Step 4: Set Up Supabase in Your Figma App

#### Install Supabase Client

If using Figma's dev mode with React/Next.js:

```bash
npm install @supabase/supabase-js
```

#### Create Supabase Config File

Create a file `lib/supabase.js` (or `utils/supabase.ts`):

```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://skfraijnuefuquyxnced.supabase.co'
const supabaseAnonKey = 'YOUR_ANON_KEY_HERE' // From Step 1

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### Step 5: Test Your Connection

Create a test component to verify the connection:

```jsx
import { useEffect, useState } from 'react'
import { supabase } from './lib/supabase'

function TestConnection() {
  const [stats, setStats] = useState(null)
  
  useEffect(() => {
    async function test() {
      const { data, error } = await supabase
        .from('season_stats')
        .select('*')
        .eq('season', '2025-26')
        .single()
      
      if (error) {
        console.error('Connection error:', error)
      } else {
        console.log('Success!', data)
        setStats(data)
      }
    }
    test()
  }, [])
  
  return (
    <div>
      {stats ? (
        <div>
          <h1>✅ Connected to Supabase!</h1>
          <p>Record: {stats.wins}-{stats.losses}</p>
          <p>Units: {stats.units}</p>
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  )
}
```

---

## 📊 Data Structure Reference

### Predictions Table Schema

```typescript
interface Prediction {
  // Required fields
  id: string                    // UUID
  date: string                  // "2026-02-19"
  home_team: string             // "Lakers"
  away_team: string             // "Warriors"
  pick: string                  // "Lakers -5.5"
  spread: number                // -5.5
  edge: number                  // 8.5 (percentage)
  confidence: string            // "high" | "medium" | "low"
  result: string | null         // "WIN" | "LOSS" | "PUSH" | null
  
  // Optional fields
  home_score?: number           // 112
  away_score?: number           // 108
  sport?: string                // "NBA"
  game_time?: string            // "7:30 PM ET"
  odds?: string                 // "-110"
  analysis?: string             // "Lakers strong at home..."
  ml_probability?: number       // 62.5 (0-100 scale)
  implied_probability?: number  // 54.0 (0-100 scale)
  
  // Metadata
  created_at: string
  updated_at: string
}
```

### Season Stats Table Schema

```typescript
interface SeasonStats {
  id: number
  season: string                // "2025-26"
  wins: number                  // 173
  losses: number                // 152
  total_games: number           // 325
  win_percentage: number        // 53.23
  units: number                 // 14.36
  roi: number                   // 4.42
  start_date: string            // "2025-10-24"
  end_date: string              // "2026-02-11"
  last_updated: string
  created_at: string
}
```

---

## 🎨 Figma-Specific Tips

### Using with Figma Dev Mode

If you're using Figma's dev mode to generate React components:

1. **Install dependencies** in your project
2. **Create a data layer** (e.g., `hooks/useNBAData.js`)
3. **Connect components** to live data instead of mock data
4. **Handle loading states** (Figma doesn't generate these)

### Example Custom Hook

```jsx
// hooks/useNBAData.js
import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'

export function useTodaysPicks() {
  const [picks, setPicks] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    async function load() {
      const today = new Date().toISOString().split('T')[0]
      const { data } = await supabase
        .from('predictions')
        .select('*')
        .eq('date', today)
        .order('edge', { ascending: false })
      
      setPicks(data || [])
      setLoading(false)
    }
    load()
  }, [])
  
  return { picks, loading }
}

export function useSeasonStats() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    async function load() {
      const { data } = await supabase
        .from('season_stats')
        .select('*')
        .eq('season', '2025-26')
        .single()
      
      setStats(data)
      setLoading(false)
    }
    load()
  }, [])
  
  return { stats, loading }
}
```

Then use in your Figma components:

```jsx
function StatsCard() {
  const { stats, loading } = useSeasonStats()
  
  if (loading) return <Skeleton />
  
  return (
    <div>
      <h2>Season Record</h2>
      <p>{stats.wins}-{stats.losses}</p>
      <p>{stats.win_percentage}% Win Rate</p>
      <p>{stats.units > 0 ? '+' : ''}{stats.units}u</p>
    </div>
  )
}
```

---

## 🔄 Daily Data Updates

Your data will automatically update when you run your daily prediction workflow:

```bash
# This runs automatically via GitHub Actions daily
python src/daily_update.py
python src/sync_to_supabase.py --mode all
```

Your Figma app will fetch the latest data on each page load, or you can add realtime subscriptions:

```javascript
// Subscribe to new predictions
const channel = supabase
  .channel('predictions')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'predictions' },
    (payload) => {
      console.log('New prediction:', payload.new)
      // Update your UI
    }
  )
  .subscribe()
```

---

## 📚 Additional Resources

- **Query Examples**: See `docs/WEB_APP_QUERIES.md` for comprehensive examples
- **Schema Details**: See `supabase_schema.sql` for full table structure
- **Sync Script**: See `src/sync_to_supabase.py` to understand data formatting

---

## 🐛 Troubleshooting

### "Invalid API key" error
- Make sure you're using the **anon/public** key (not service_role)
- Check that the key is correctly pasted in your config file

### "Row Level Security policy violation"
- The RLS policies should allow public read access
- Run the RLS policies from `supabase_schema.sql` if needed

### Empty data
- Make sure you've run the sync script after updating the schema
- Check the Supabase dashboard table editor to verify data exists

### Type errors with TypeScript
- Generate types from Supabase: `npx supabase gen types typescript --project-id skfraijnuefuquyxnced`
- Or copy the interfaces from this guide

---

## ✅ Next Steps

1. ✅ Get anon key from Supabase
2. ✅ Update schema (fresh or migrate)
3. ✅ Re-sync data
4. ✅ Add Supabase client to Figma app
5. ✅ Test connection
6. ✅ Build your components
7. ✅ Deploy! 🚀

Need help? Check the query examples in `WEB_APP_QUERIES.md` or ask for assistance with specific components!
