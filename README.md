# VITALS — Game Health Monitor

**How broken is this game right now?**

VITALS scans Steam reviews, detects technical issues, tracks player counts, and produces a diagnostic health score for any game on the Steam Store. It answers the question every gamer asks before buying: "Is this game running well, or should I wait?"

> **Live import demo:** Search any Steam game by name, hit Import, and VITALS fetches reviews, detects issues, records player counts, and generates a health score — all from real Steam data.

---

## Business Logic

### The Problem

Steam reviews mix opinions ("this game is fun") with stability reports ("it crashes every 10 minutes"). Review aggregators and Metacritic can't tell you if a game is **broken**. Gamers rely on patch notes, Reddit threads, and word-of-mouth to figure out whether it's safe to buy.

### The Solution

VITALS treats every Steam game like a patient in triage. It:

1. **Ingests real Steam reviews** — categorizing them by issue type (crashes, freezes, FPS drops, disconnect, etc.)
2. **Tracks player counts** — retention tells you if people are leaving
3. **Detects incident patterns** — extracts the actual complaint sentences as evidence
4. **Produces a health score** — weighted from sentiment, stability, retention, and Steam Deck compatibility

### Scoring Formula

```
Health Score = Sentiment × 0.45 + Stability × 0.25 + Retention × 0.20 + Deck × 0.10
```

| Score | Recommendation |
|---|---|
| 80+ | **BUY NOW** — game is healthy, real players agree |
| 60–79 | **PLAYABLE** — functional but with issues |
| 40–59 | **WAIT FOR PATCHES** — significant problems reported |
| <40 | **AVOID FOR NOW** — widespread instability |

### Who Is This For?

- Gamers checking stability before purchasing
- Developers monitoring their game's health post-launch
- Publishers tracking competitor launches
- Content creators needing data-backed "should you buy" verdicts

---

## System Architecture

```
┌──────────────────────┐     ┌──────────────────────────────────┐
│   Next.js Frontend   │────▶│         FastAPI Backend           │
│   (TypeScript)        │     │         (Python 3.11)            │
│                      │     │                                  │
│  • Home + Game List   │     │  • Games API (CRUD + health)     │
│  • Game Detail Page   │     │  • Steam Metadata Importer       │
│  • Admin Dashboard    │     │  • Review Ingestion Pipeline      │
│  • Steam Search +      │     │  • Issue Detection Engine        │
│    Import UI          │     │  • Sentiment Engine              │
│  • Health Gauge        │     │  • Player Retention Service      │
│                      │     │  • Health Score Algorithm         │
└──────────────────────┘     │  • Cron Job Scheduler            │
                              │  • PostgreSQL + Redis             │
                              └──────────────────────────────────┘
```

### Data Flow

```
Steam API ──▶ Steam Importer ──▶ games table
                                    │
Steam API ──▶ Review Pipeline ──▶ reviews table ──▶ Issue Detection ──▶ issue_reports
                                                     │
Steam API ──▶ Player Count ──▶ player_metrics ──▶ Retention Calc
                                                         │
                                    ┌────────────────────┘
                                    ▼
                          Health Score Algorithm
                                    │
                                    ▼
                          health_scores table
                                    │
                                    ▼
                          Public API ──▶ Frontend
```

### Database Schema

```
games            — Game metadata (steam_app_id, name, developer, platforms, genre,
                   cover_url, steam_deck_status, controller_support)
reviews          — Steam reviews (review_id, game_id, review_text, recommended,
                   playtime, created_at)
health_scores    — Historical health snapshots (game_id, score, sentiment,
                   stability, retention, recommendation, created_at)
issue_reports    — Detected issues (game_id, review_id, issue_type, summary)
player_metrics   — Player count snapshots (game_id, current_players,
                   peak_players, recorded_at)
patches          — Patch note records (game_id, version, bug_fixes,
                   performance_fixes, server_fixes)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Monorepo** | Turborepo + pnpm workspaces |
| **Frontend** | Next.js 14 (App Router), React 18, TypeScript |
| **Styling** | Tailwind CSS 3, CSS custom properties |
| **Fonts** | Press Start 2P (logo/recommendations), Instrument Serif (scores), DM Sans (UI), JetBrains Mono (data) |
| **Backend** | FastAPI (Python 3.11) |
| **ORM** | SQLAlchemy 2.0 + Alembic (migrations) |
| **Database** | PostgreSQL 16 |
| **Cache** | Redis 7 |
| **Job Scheduler** | APScheduler |
| **HTTP Client** | httpx (async) |
| **Containerization** | Docker Compose |
| **Shared Types** | TypeScript package (`@game-health/types`) |

---

## Installation & Setup

### Prerequisites

- **Node.js** ≥ 18
- **pnpm** ≥ 9.0
- **Python** ≥ 3.11
- **PostgreSQL** ≥ 16
- **Redis** 7 (optional, for caching)
- **Docker** + Docker Compose (recommended)

### Quick Start (Docker)

```bash
# Clone the repo
git clone https://github.com/yourusername/game-health-monitor.git
cd game-health-monitor

# Start PostgreSQL + Redis + API
cp .env.example .env
docker compose up -d

# Install frontend dependencies
pnpm install

# Start the frontend
pnpm dev
```

Visit `http://localhost:3000` for the frontend and `http://localhost:8000/docs` for the API docs.

### Manual Setup (macOS / Linux)

```bash
# 1. Install PostgreSQL
brew install postgresql@16
brew services start postgresql@16
createdb game_health

# 2. Install frontend dependencies
pnpm install

# 3. Set up Python backend
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Run database migrations
PYTHONPATH=$(pwd) alembic upgrade head

# 5. Start the API server
PYTHONPATH=$(pwd) uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 6. In a new terminal, start the frontend
cd ../..
pnpm dev
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/game_health
REDIS_URL=redis://localhost:6379
STEAM_API_KEY=          # Optional, for official Steam Web API
IGDB_CLIENT_ID=         # Optional, for IGDB enrichment
IGDB_CLIENT_SECRET=     # Optional, for IGDB enrichment
NEXT_PUBLIC_API_URL=http://localhost:8000
```

> **Note:** The Steam Store API (`store.steampowered.com/api/appdetails`) and review API (`store.steampowered.com/appreviews`) are public and do not require an API key. The `STEAM_API_KEY` is only needed for partner-level Web API endpoints.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | API health check |
| `GET` | `/games` | List all games (sort: name, score, worst) |
| `GET` | `/games/{id}` | Game detail with health score |
| `GET` | `/games/{id}/health` | Health score timeline |
| `GET` | `/games/{id}/issues` | Issue breakdown with incident summaries |
| `GET` | `/games/{id}/recommendation` | Recommendation + score breakdown |
| `GET` | `/steam/search?query=` | Search Steam Store |
| `POST` | `/games/import/{steam_app_id}` | Import game by Steam app ID |
| `POST` | `/games/import/search` | Import game by name search |
| `POST` | `/games/import` | Batch import (body: `{"steam_app_ids":[730,440]}`) |
| `POST` | `/games/{id}/score` | Recalculate health score |
| `GET` | `/admin/status` | System statistics |
| `POST` | `/admin/sync` | Rescore all games |

---

## Monorepo Structure

```
game-health-monitor/
├── apps/
│   ├── web/                    # Next.js 14 (TypeScript)
│   │   ├── src/
│   │   │   ├── app/            # Pages (App Router)
│   │   │   │   ├── page.tsx         # Home
│   │   │   │   ├── games/[id]/      # Game detail
│   │   │   │   └── admin/           # Admin dashboard
│   │   │   ├── components/     # React components
│   │   │   │   ├── health-gauge.tsx   # Radial SVG score gauge
│   │   │   │   ├── game-card.tsx      # Game card with deck/score badges
│   │   │   │   ├── game-browser.tsx   # Game list + sections
│   │   │   │   ├── steam-search.tsx   # Live Steam search + import
│   │   │   │   └── rescore-button.tsx # Score recalculation
│   │   │   └── lib/api.ts      # Fetch wrapper
│   │   └── tailwind.config.ts
│   │
│   └── api/                    # FastAPI (Python)
│       ├── src/
│       │   ├── main.py         # FastAPI app entry
│       │   ├── config.py       # Settings from env
│       │   ├── database.py     # SQLAlchemy engine
│       │   ├── models/         # 6 ORM models
│       │   ├── routers/        # API endpoints
│       │   ├── services/       # 10 business logic services
│       │   └── jobs/           # Cron scheduler
│       └── alembic/            # Database migrations
│
├── packages/
│   ├── types/                  # @game-health/types (shared TS)
│   └── eslint-config/          # @game-health/eslint-config
│
├── docker-compose.yml          # PostgreSQL 16 + Redis 7 + API
├── turbo.json                  # Turborepo pipeline
├── pnpm-workspace.yaml
└── README.md
```

---

## Deployment

### Frontend (Vercel — recommended)

```bash
# Install Vercel CLI
npm i -g vercel
vercel --prod
```

Set `NEXT_PUBLIC_API_URL` to your deployed API URL.

### Backend (Docker + any cloud VM)

```bash
docker compose -f docker-compose.prod.yml up -d
```

The FastAPI backend runs on `:8000`. Use nginx or a cloud load balancer for SSL termination.

### GitHub Pages (static export only)

For a static portfolio build:

```bash
cd apps/web
pnpm build  # static HTML/CSS/JS output
# Deploy .next/standalone or out/ to GitHub Pages
```

> **Note:** The live import feature requires the FastAPI backend. For a fully static demo, the app shows the last-cached game data.

---

## Key Features

### Real-Time Steam Integration
- Search any game on Steam by name
- Import metadata (name, developer, publisher, genre, platforms, cover art)
- Fetch actual Steam reviews with cursor-based pagination
- Track current player counts from Steam's official API

### Issue Detection Engine
- **7 categories:** crash, freeze, stutter, FPS, disconnect, save corruption, server
- Regex-based pattern matching with sentence extraction
- Incident summaries sourced from real review text

### Health Gauge
- Radial SVG gauge with animated score fill
- Color shifts based on health tier (green/yellow/orange/red)
- Recommendation badge links directly to the Steam Store page

### Cron Jobs
- **Every 6 hours:** Ingest new reviews
- **Daily:** Recalculate health scores for all tracked games

---

## Design Philosophy

VITALS uses a dark, minimal clinical aesthetic. The interface treats game health like medical diagnostics — raw numbers, clean typography, and a radial gauge that feels like reading vital signs. No gradients, no decoration, no AI-slur aesthetics.

- **Fonts:** Press Start 2P for the logo and recommendations (pixelated, retro-gaming feel); Instrument Serif for score display; DM Sans for body text; JetBrains Mono for data readouts
- **Color:** Health-driven palette — green (80+), yellow (60+), orange (40+), red (<40)
- **Layout:** Horizontal scroll for Recently Added, sparse grids for all games, full-bleed cover art on detail pages

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a pull request

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

Built with ❤️ for gamers who want to know what they're getting into.
