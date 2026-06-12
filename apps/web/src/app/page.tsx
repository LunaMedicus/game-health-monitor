import type { Game } from "@game-health/types";
import { apiFetch } from "@/lib/api";
import { GameBrowser } from "@/components/game-browser";

export default async function Home() {
  let games: (Game & { health_score?: number; recommendation?: string })[] = [];
  try {
    games = await apiFetch<(Game & { health_score?: number; recommendation?: string })[]>("/games?sort=score");
  } catch {
    games = [];
  }

  return (
    <main className="min-h-screen">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="mb-16">
          <h1 className="font-display text-4xl italic text-text mb-3">
            vitals
          </h1>
          <p className="text-muted text-lg">
            How broken is this game right now?
          </p>
          <p className="text-very-muted text-sm font-mono mt-2">
            Scanning {games.length} games · Sentiment 45% + Stability 25% + Retention 20% + Deck 10%
          </p>
        </div>

        <GameBrowser initialGames={games} />
      </div>
    </main>
  );
}
