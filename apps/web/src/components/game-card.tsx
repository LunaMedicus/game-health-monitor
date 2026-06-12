import type { Game } from "@game-health/types";
import Link from "next/link";
import { HealthBadge } from "./health-gauge";

interface GameCardProps {
  game: Game & { health_score?: number; recommendation?: string; steam_deck_status?: string | null };
}

export function GameCard({ game }: GameCardProps) {
  const score = game.health_score ?? null;
  const deck = game.steam_deck_status ?? null;

  return (
    <Link href={`/games/${game.id}`}>
      <div className="card-hover group flex items-start gap-3 p-3 rounded-lg border border-border bg-surface cursor-pointer">
        {game.cover_url ? (
          <img
            src={game.cover_url}
            alt={game.name}
            className="w-12 h-16 object-cover rounded flex-shrink-0"
          />
        ) : (
          <div className="w-12 h-16 rounded bg-surface-raised flex-shrink-0 flex items-center justify-center">
            <span className="font-mono text-[10px] text-very-muted">NO IMG</span>
          </div>
        )}
        <div className="flex-1 min-w-0">
          <h3 className="font-sans text-[15px] font-semibold text-text leading-tight truncate group-hover:text-cyan transition-colors">
            {game.name}
          </h3>
          <p className="text-[13px] text-muted mt-0.5 truncate">
            {game.developer && game.developer}
            {game.release_date && ` · ${game.release_date}`}
          </p>
          <div className="flex items-center gap-2 mt-2 flex-wrap">
            {score !== null && <HealthBadge score={score} recommendation={game.recommendation} steamAppId={game.steam_app_id} />}
            {deck && (
              <span className={`font-pixel text-[8px] tracking-tighter px-1.5 py-0.5 rounded border ${
                deck === "verified" ? "border-healthy/30 text-healthy" : "border-playable/30 text-playable"
              }`}>
                DECK
              </span>
            )}
            {game.genre && (
              <span className="text-[11px] text-very-muted font-mono">
                {game.genre}
              </span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
