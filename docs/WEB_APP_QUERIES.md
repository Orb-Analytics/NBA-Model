# 🌐 Supabase Queries for Your Figma Web App

## ✅ Schema Update
**This guide has been updated to match your Figma app's schema requirements.**

---

## Setup in Your Figma/Web App

### 1. Install Supabase Client

```bash
npm install @supabase/supabase-js
```

### 2. Initialize Supabase

```javascript
import { createClient } from '@supabase/supabase-js'

// Use your ANON/PUBLIC key (NOT service_role) for web apps
const supabaseUrl = 'https://skfraijnuefuquyxnced.supabase.co'
const supabaseAnonKey = 'your-anon-public-key-here' // Get from Supabase → Settings → API

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

**Important:** The `supabaseAnonKey` is safe to use in frontend code. It has read-only access via Row Level Security (RLS).

---

## Common Queries

### 📊 Get Current Season Stats

```javascript
async function getSeasonStats() {
  const { data, error } = await supabase
    .from('season_stats')
    .select('*')
    .eq('season', '2025-26')
    .single()
  
  if (error) {
    console.error('Error:', error)
    return null
  }
  
  return data
  // Returns: { wins: 173, losses: 152, win_percentage: 53.23, units: 14.36, roi: 4.42, ... }
}
```

### 🏀 Get Today's Picks

```javascript
async function getTodaysPicks() {
  const today = new Date().toISOString().split('T')[0] // YYYY-MM-DD
  
  const { data, error } = await supabase
    .from('predictions')
    .select('*')
    .eq('date', today)
    .order('edge', { ascending: false })
  
  return data || []
  // Returns array like:
  // [
  //   { date: '2026-02-19', home_team: 'Lakers', away_team: 'Warriors', 
  //     pick: 'Lakers -5.5', spread: -5.5, edge: 8.5, confidence: 'high', 
  //     result: null, odds: '-110', ... }
  // ]
}
```

### 📈 Get Recent Results (Last 10 Games)

```javascript
async function getRecentResults() {
  const { data, error } = await supabase
    .from('predictions')
    .select('*')
    .in('result', ['WIN', 'LOSS', 'PUSH'])
    .order('date', { ascending: false })
    .limit(10)
  
  return data || []
  // Each item has: pick, spread, edge, confidence, result, home_score, away_score, etc.
}
```

### 🎯 Get High Confidence Picks

```javascript
async function getHighConfidencePicks() {
  const { data, error } = await supabase
    .from('predictions')
    .select('*')
    .or('confidence.eq.high,edge.gte.8.0')
    .order('date', { ascending: false })
    .limit(20)
  
  return data || []
  // Returns picks where confidence='high' OR edge >= 8%
}

```javascript
async function getHighConfidencePicks() {
  const { data, error } = await supabase
    .from('predictions')
    .select('*')
    .gte('edge', 5.0)
    .order('date', { ascending: false })
    .limit(20)
  
  return data || []
}
```

### 📅 Get Last 7 Days of Picks

```javascript
async function getLastWeekPicks() {
  const sevenDaysAgo = new Date()
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
  const dateStr = sevenDaysAgo.toISOString().split('T')[0]
  
  const { data, error } = await supabase
    .from('predictions')
    .select('*')
    .gte('date', dateStr)
    .order('date', { ascending: false })
  
  return data || []
}
```

### 🏆 Get Picks by Team

```javascript
async function getPicksByTeam(teamName) {
  const { data, error } = await supabase
    .from('predictions')
    .select('*')
    .eq('pick_team', teamName)
    .order('date', { ascending: false })
    .limit(20)
  
  return data || []
  // Example: getPicksByTeam('Golden State')
}
```

### 📊 Get Win/Loss Breakdown by Date

```javascript
async function getWinLossBreakdown() {
  const { data, error } = await supabase
    .from('predictions')
    .select('date, result')
    .in('result', ['WIN', 'LOSS'])
    .order('date', { ascending: false })
  
  if (!data) return []
  
  // Group by date
  const breakdown = {}
  data.forEach(pick => {
    if (!breakdown[pick.date]) {
      breakdown[pick.date] = { date: pick.date, wins: 0, losses: 0, total: 0 }
    }
    breakdown[pick.date].total++
    if (pick.result === 'WIN') breakdown[pick.date].wins++
    else breakdown[pick.date].losses++
  })
  
  return Object.values(breakdown)
}
```

---

## React Component Examples

### Season Stats Card

```jsx
import { useEffect, useState } from 'react'
import { supabase } from './supabase'

function SeasonStatsCard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    async function loadStats() {
      const { data } = await supabase
        .from('season_stats')
        .select('*')
        .eq('season', '2025-26')
        .single()
      
      setStats(data)
      setLoading(false)
    }
    
    loadStats()
  }, [])
  
  if (loading) return <div>Loading...</div>
  if (!stats) return <div>No stats available</div>
  
  return (
    <div className="stats-card">
      <h2>🏀 Season Performance</h2>
      <div className="stat-row">
        <span className="label">Record:</span>
        <span className="value">{stats.wins}-{stats.losses}</span>
      </div>
      <div className="stat-row">
        <span className="label">Win %:</span>
        <span className="value">{stats.win_percentage.toFixed(1)}%</span>
      </div>
      <div className="stat-row">
        <span className="label">Units:</span>
        <span className={`value ${stats.units >= 0 ? 'positive' : 'negative'}`}>
          {stats.units > 0 ? '+' : ''}{stats.units.toFixed(2)}u
        </span>
      </div>
      <div className="stat-row">
        <span className="label">ROI:</span>
        <span className={`value ${stats.roi >= 0 ? 'positive' : 'negative'}`}>
          {stats.roi > 0 ? '+' : ''}{stats.roi.toFixed(2)}%
        </span>
      </div>
    </div>
  )
}
```

### Today's Picks List

```jsx
function TodaysPicks() {
  const [picks, setPicks] = useState([])
  
  useEffect(() => {
    async function loadPicks() {
      const today = new Date().toISOString().split('T')[0]
      const { data } = await supabase
        .from('predictions')
        .select('*')
        .eq('date', today)
        .order('edge', { ascending: false })
      
      setPicks(data || [])
    }
    
    loadPicks()
  }, [])
  
  if (picks.length === 0) {
    return <div>No picks for today</div>
  }
  
  return (
    <div className="picks-list">
      <h2>🎯 Today's Picks</h2>
      {picks.map(pick => (
        <div key={pick.id} className={`pick-card confidence-${pick.confidence}`}>
          <div className="pick-header">
            <h3>{pick.pick}</h3>
            <span className={`confidence-badge ${pick.confidence}`}>
              {pick.confidence === 'high' ? '🔥' : pick.confidence === 'medium' ? '⚡' : ''}
              {pick.confidence.toUpperCase()}
            </span>
          </div>
          <div className="matchup">
            <span>{pick.away_team} @ {pick.home_team}</span>
            {pick.game_time && <span className="time">{pick.game_time}</span>}
          </div>
          <div className="pick-details">
            <div className="stat">
              <span className="label">Edge:</span>
              <span className="value">{pick.edge.toFixed(1)}%</span>
            </div>
            <div className="stat">
              <span className="label">Odds:</span>
              <span className="value">{pick.odds}</span>
            </div>
            {pick.ml_probability && (
              <div className="stat">
                <span className="label">Model:</span>
                <span className="value">{pick.ml_probability.toFixed(1)}%</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
```

### Recent Results Feed

```jsx
function RecentResults() {
  const [results, setResults] = useState([])
  
  useEffect(() => {
    async function loadResults() {
      const { data } = await supabase
        .from('predictions')
        .select('*')
        .in('result', ['WIN', 'LOSS', 'PUSH'])
        .order('date', { ascending: false })
        .limit(10)
      
      setResults(data || [])
    }
    
    loadResults()
  }, [])
  
  return (
    <div className="results-feed">
      <h3>📊 Recent Results</h3>
      {results.map(result => (
        <div key={result.id} className={`result-item ${result.result?.toLowerCase()}`}>
          <div className="result-header">
            <span className="icon">
              {result.result === 'WIN' ? '✅' : result.result === 'LOSS' ? '❌' : '➖'}
            </span>
            <span className="date">{result.date}</span>
            <span className={`badge ${result.result?.toLowerCase()}`}>
              {result.result}
            </span>
          </div>
          <div className="result-details">
            <span className="pick">{result.pick}</span>
            {result.home_score !== null && (
              <span className="score">
                {result.away_team} {result.away_score} @ {result.home_team} {result.home_score}
              </span>
            )}
          </div>
          <div className="result-meta">
            <span>Edge: {result.edge.toFixed(1)}%</span>
            <span>Confidence: {result.confidence}</span>
          </div>
        </div>
      ))}
    </div>
  )
}
```

---

## Realtime Updates (Optional)

Subscribe to new predictions in real-time:

```javascript
// Subscribe to changes
const channel = supabase
  .channel('predictions-changes')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'predictions' },
    (payload) => {
      console.log('New prediction added!', payload.new)
      // Update your UI with the new prediction
    }
  )
  .subscribe()

// Unsubscribe when done
channel.unsubscribe()
```

---

## Error Handling

```javascript
async function safeFetchData(queryFn) {
  try {
    const data = await queryFn()
    return { data, error: null }
  } catch (error) {
    console.error('Supabase error:', error)
    return { data: null, error: error.message }
  }
}

// Usage
const { data: stats, error } = await safeFetchData(getSeasonStats)
if (error) {
  // Show error message to user
}
```

---

## Tips

1. **Use the anon/public key** in your web app (NOT service_role)
2. **Cache data** to reduce API calls - use React Query or SWR
3. **Handle loading states** - show skeletons while data loads
4. **Error boundaries** - catch and display errors gracefully
5. **Refresh data** after important events (new picks posted, etc.)

Your Supabase database is ready to power your web app! 🚀
