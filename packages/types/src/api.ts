import type { Game, HealthScore, IssueReport } from "./game";

export interface GameDetail extends Game {
  health_score?: number;
  recommendation?: string;
  top_issues?: IssueReport[];
  sentiment?: number;
  stability?: number;
  retention?: number;
}

export interface GamesResponse {
  games: GameDetail[];
}

export interface GameDetailResponse extends GameDetail {}
