"use client";

import { useState } from "react";
import type { Game } from "@game-health/types";
import { GameCard } from "@/components/game-card";
import { SteamSearch } from "@/components/steam-search";

type GameWithHealth = Game & {
  health_score?: number;
  recommendation?: string;
};

interface GameBrowserProps {
  initialGames: GameWithHealth[];
}

export function GameBrowser({ initialGames }: GameBrowserProps) {
  const [games, setGames] = useState(initialGames);
  const [sessionImports, setSessionImports] = useState<GameWithHealth[]>([]);

  function handleImported(game: GameWithHealth) {
    setSessionImports((current) => {
      const withoutDuplicate = current.filter((g) => g.id !== game.id);
      return [game, ...withoutDuplicate].slice(0, 6);
    });
    setGames((current) => {
      const withoutDuplicate = current.filter((g) => g.id !== game.id);
      return [game, ...withoutDuplicate];
    });
  }

  const healthy = games.filter((g) => (g.health_score ?? 0) >= 80);
  const struggling = games.filter((g) => {
    const s = g.health_score ?? 0;
    return s >= 40 && s < 80;
  });
  const worst = games.filter((g) => (g.health_score ?? 0) < 40);

  const recent = [
    ...sessionImports,
    ...[...games]
      .sort((a, b) => (b.id ?? 0) - (a.id ?? 0))
      .filter((g) => !sessionImports.some((imported) => imported.id === g.id)),
  ].slice(0, 6);

  return (
    <>
      <SteamSearch onImported={handleImported} />

      {games.length === 0 ? (
        <div className="text-center py-20 text-very-muted">
          <p className="text-xl mb-2">No games tracked yet</p>
          <p className="font-mono text-sm">Search Steam above to scan your first game.</p>
        </div>
      ) : (
        <>
          {/* Recently Added */}
          {recent.length > 0 && (
            <section className="mb-12">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-sans text-sm font-semibold text-muted uppercase tracking-wider">
                  Recently Added
                </h2>
                <span className="font-mono text-xs text-very-muted">
                  {recent.length} games
                </span>
              </div>
              <div className="flex gap-3 overflow-x-auto pb-2 -mx-6 px-6 scrollbar-hide">
                {recent.map((game) => (
                  <div key={game.id} className="flex-shrink-0 w-64">
                    <GameCard game={game} />
                  </div>
                ))}
              </div>
            </section>
          )}

          <div className="section-divider mb-12" />

          {/* Top Healthy */}
          {healthy.length > 0 && (
            <section className="mb-12">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-sans text-sm font-semibold text-muted uppercase tracking-wider">
                  Healthy
                </h2>
                <span className="font-mono text-xs text-very-muted">
                  {healthy.length} games
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {healthy.map((game) => (
                  <GameCard key={game.id} game={game} />
                ))}
              </div>
            </section>
          )}

          {/* Struggling */}
          {struggling.length > 0 && (
            <section className="mb-12">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-sans text-sm font-semibold text-muted uppercase tracking-wider">
                  Needs Improvement
                </h2>
                <span className="font-mono text-xs text-very-muted">
                  {struggling.length} games
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {struggling.map((game) => (
                  <GameCard key={game.id} game={game} />
                ))}
              </div>
            </section>
          )}

          {/* Worst */}
          {worst.length > 0 && (
            <section className="mb-12">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-sans text-sm font-semibold text-muted uppercase tracking-wider">
                  Avoid
                </h2>
                <span className="font-mono text-xs text-very-muted">
                  {worst.length} games
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {worst.map((game) => (
                  <GameCard key={game.id} game={game} />
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </>
  );
}
