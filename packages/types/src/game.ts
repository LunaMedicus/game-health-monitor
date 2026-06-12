export interface Game {
  id: number;
  steam_app_id: number | null;
  igdb_id: number | null;
  name: string;
  release_date: string | null;
  developer: string | null;
  publisher: string | null;
  cover_url: string | null;
  platforms: string | null;
  genre: string | null;
  steam_deck_status: string | null;
  controller_support: string | null;
}

export interface Review {
  id: number;
  review_id: string;
  game_id: number;
  review_text: string | null;
  recommended: boolean;
  playtime: number | null;
  created_at: string | null;
}

export interface PlayerMetric {
  id: number;
  game_id: number;
  current_players: number;
  peak_players: number;
  retention_30d: number | null;
  retention_90d: number | null;
  recorded_at: string;
}

export interface HealthScore {
  id: number;
  game_id: number;
  score: number;
  sentiment: number;
  stability: number;
  retention: number;
  developer_support: number;
  recommendation: string;
  created_at: string;
}

export interface IssueReport {
  id: number;
  game_id: number;
  review_id: number | null;
  issue_type: string;
  confidence: number;
}

export interface Patch {
  id: number;
  game_id: number;
  version: string | null;
  title: string | null;
  notes: string | null;
  bug_fixes: string | null;
  performance_fixes: string | null;
  server_fixes: string | null;
  released_at: string | null;
}
