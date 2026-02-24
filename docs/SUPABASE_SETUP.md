# 🔗 Supabase Integration for Web App

Connect your NBA prediction model data to Supabase for your Figma web app.

## 🎯 What Gets Synced

1. **Daily Predictions** - Today's picks with spreads, odds, and edge calculations
2. **Historical Results** - All past predictions with WIN/LOSS results
3. **Season Stats** - Current record, units, ROI, win percentage

---

## 📋 Setup Steps

### 1. Create Supabase Tables

1. Go to your Supabase project
2. Click **SQL Editor** in the sidebar
3. Create a new query
4. Copy and paste the contents of `supabase_schema.sql`
5. Click **Run** to create tables, views, and policies

This creates:
- `predictions` table - All picks and results
- `season_stats` table - Performance statistics
- Views for easy querying (`todays_picks`, `recent_results`, etc.)
- Row Level Security policies (public read, authenticated write)

### 2. Add Supabase Credentials to GitHub Secrets

1. Go to your Supabase project **Settings** → **API**
2. Copy your **Project URL** (e.g., `https://yourproject.supabase.co`)
3. Copy your **anon/public** key (for read access from web app)
4. Copy your **service_role** key (for write access from sync script)

5. Add to GitHub Secrets:
   - `SUPABASE_URL` = Your project URL or just project ID (e.g., `skfraijnuefuquyxnced`)
   - `SUPABASE_KEY` = Your **service_role** key (for API sync)
   - `SUPABASE_ANON_KEY` = Your **anon** key (for web app read access)

### 3. Test the Sync Script

```bash
# Dry run - preview what would be synced
python src/sync_to_supabase.py --dry-run

# Sync only today's predictions
python src/sync_to_supabase.py --mode daily

# Sync historical results (last 50 games for testing)
python src/sync_to_supabase.py --mode historical --limit 50

# Sync season stats
python src/sync_to_supabase.py --mode stats

# Sync everything
python src/sync_to_supabase.py --mode all
```

---

## 🔄 Automated Daily Sync

Add this step to your `.github/workflows/daily_predictions.yml` workflow:

```yaml
- name: 🔗 Sync to Supabase
  env:
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
  run: |
    echo "📤 Syncing data to Supabase..."
    python src/sync_to_supabase.py --mode all
```

---

## 🌐 Using in Your Web App

### Connect to Supabase (JavaScript/React)

```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://yourproject.supabase.co',
  'your-anon-key' // Use SUPABASE_ANON_KEY
)

// Get today's picks
const { data: picks } = await supabase
  .from('todays_picks')
  .select('*')

// Get season stats
const { data: stats } = await supabase
  .from('season_stats')
  .select('*')
  .eq('season', '2025-26')
  .single()

// Get last 7 days of results
const { data: recent } = await supabase
  .from('predictions')
  .select('*')
  .gte('date', new Date(Date.now() - 7*24*60*60*1000).toISOString())
  .order('date', { ascending: false })
```

### Realtime Updates (Optional)

```javascript
// Subscribe to new predictions
supabase
  .channel('predictions')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'predictions' }, 
    payload => {
      console.log('New prediction!', payload.new)
    }
  )
  .subscribe()
```

---

## 📊 Database Structure

### `predictions` Table
| Column | Type | Description |
|--------|------|-------------|
| id | bigserial | Primary key |
| date | date | Game date |
| home_team | text | Home team name |
| away_team | text | Away team name |
| pick_team | text | Picked team |
| pick_side | text | FAVORITE or UNDERDOG |
| spread | numeric | Spread value |
| odds | numeric | American odds (-110, +150, etc.) |
| edge | numeric | Edge percentage (3.2 = 3.2%) |
| model_prob | numeric | Model probability (%) |
| implied_prob | numeric | Implied probability (%) |
| result | text | WIN, LOSS, or PENDING |
| actual_cover | integer | 1 if covered, 0 if not, null if pending |

### `season_stats` Table
| Column | Type | Description |
|--------|------|-------------|
| season | text | Season identifier (2025-26) |
| wins | integer | Total wins |
| losses | integer | Total losses |
| total_games | integer | Total games |
| win_percentage | numeric | Win % |
| units | numeric | Total units won/lost |
| roi | numeric | Return on investment % |
| start_date | date | First game date |
| end_date | date | Last game date |
| last_updated | timestamptz | Last sync time |

---

## 🔒 Security Notes

- **Public Read Access**: Anyone can read predictions (good for web app)
- **Authenticated Write**: Only your API (with service_role key) can update data
- **Never expose** your `service_role` key in frontend code
- Use `anon` key in your web app (read-only access)

---

## 🐛 Troubleshooting

**Issue**: `Missing SUPABASE_URL or SUPABASE_KEY`
- Make sure secrets are added to GitHub Secrets
- For local testing, set environment variables:
  ```bash
  export SUPABASE_URL="https://yourproject.supabase.co"
  export SUPABASE_KEY="your-service-role-key"
  ```

**Issue**: `403 Forbidden` errors
- Check your RLS policies are enabled
- Make sure you're using the `service_role` key for API sync
- Verify the key has write permissions

**Issue**: No data showing in web app
- Run sync manually: `python src/sync_to_supabase.py --mode all`
- Check Supabase Table Editor to verify data exists
- Verify you're using the correct `anon` key in frontend

---

## 📱 Example Web App Components

### Today's Picks Card
```jsx
function TodaysPicks() {
  const [picks, setPicks] = useState([])
  
  useEffect(() => {
    async function loadPicks() {
      const { data } = await supabase
        .from('todays_picks')
        .select('*')
      setPicks(data || [])
    }
    loadPicks()
  }, [])
  
  return (
    <div>
      <h2>🏀 Today's Picks</h2>
      {picks.map(pick => (
        <div key={pick.id}>
          <strong>{pick.pick_team} {pick.spread > 0 ? '+' : ''}{pick.spread}</strong>
          <span>vs {pick.home_team === pick.pick_team ? pick.away_team : pick.home_team}</span>
          <span>Edge: {pick.edge}%</span>
        </div>
      ))}
    </div>
  )
}
```

### Season Stats Display
```jsx
function SeasonStats() {
  const [stats, setStats] = useState(null)
  
  useEffect(() => {
    async function loadStats() {
      const { data } = await supabase
        .from('season_stats')
        .select('*')
        .eq('season', '2025-26')
        .single()
      setStats(data)
    }
    loadStats()
  }, [])
  
  if (!stats) return <div>Loading...</div>
  
  return (
    <div>
      <h2>📊 Season Performance</h2>
      <div>Record: {stats.wins}-{stats.losses} ({stats.win_percentage}%)</div>
      <div>Units: {stats.units > 0 ? '+' : ''}{stats.units}u</div>
      <div>ROI: {stats.roi > 0 ? '+' : ''}{stats.roi}%</div>
    </div>
  )
}
```

---

## 🎉 You're All Set!

Your NBA prediction data is now synced to Supabase and ready for your web app. The data updates automatically via GitHub Actions after each daily prediction run.
