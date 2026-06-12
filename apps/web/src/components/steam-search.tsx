"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { Game } from "@game-health/types";

interface SteamResult {
  steam_app_id: number;
  name: string;
  cover_url: string;
  price: number | null;
}

interface ImportResult {
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
  health_score: number;
  recommendation: string;
  pipeline: {
    reviews_imported: number;
    issues: Record<string, number>;
    current_players: number | null;
    score: number;
  };
}

interface SteamSearchProps {
  onImported?: (game: Game & { health_score?: number; recommendation?: string }) => void;
}

export function SteamSearch({ onImported }: SteamSearchProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SteamResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [importing, setImporting] = useState<number | null>(null);
  const [importResult, setImportResult] = useState<ImportResult | null>(null);

  async function search() {
    if (!query.trim()) return;
    setLoading(true);
    setImportResult(null);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/steam/search?query=${encodeURIComponent(query)}&limit=5`
      );
      if (!res.ok) throw new Error("Search failed");
      const data = await res.json();
      setResults(data);
    } catch {
      setImportResult(null);
    } finally {
      setLoading(false);
    }
  }

  async function importBySteamAppId(result: SteamResult, index: number) {
    setImporting(index);
    setImportResult(null);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/games/import/${result.steam_app_id}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        }
      );
      const data = await res.json();
      if (data.error) {
        setImportResult(null);
      } else {
        setImportResult(data);
        setResults([]);
        setQuery("");
        onImported?.(data);
        router.refresh();
      }
    } catch {
      setImportResult(null);
    } finally {
      setImporting(null);
    }
  }

  const scoreColor = importResult
    ? importResult.health_score >= 80
      ? "text-healthy"
      : importResult.health_score >= 60
        ? "text-playable"
        : "text-danger"
    : "";

  const scoreBg = importResult
    ? importResult.health_score >= 80
      ? "bg-healthy/10"
      : importResult.health_score >= 60
        ? "bg-playable/10"
        : "bg-danger/10"
    : "";

  return (
    <div className="mb-16">
      <div className="flex gap-3">
        <div className="flex-1 relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && search()}
            placeholder="Search Steam..."
            className="w-full bg-surface border border-border rounded-lg px-4 py-3 text-sm text-text placeholder:text-very-muted font-mono focus:outline-none focus:border-border-active transition-colors"
          />
        </div>
        <button
          onClick={search}
          disabled={loading}
          className="bg-surface border border-border rounded-lg px-6 py-3 text-sm font-sans font-medium text-text hover:bg-surface-raised hover:border-border-active transition-colors disabled:opacity-50"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {importResult && (
        <div className="mt-4 border border-border rounded-lg p-5 bg-surface">
          <div className="flex items-center gap-4 mb-4">
            <div className={`font-display text-3xl ${scoreColor}`}>
              {importResult.health_score}
            </div>
            <div>
              <p className="font-sans font-semibold text-text">{importResult.name}</p>
              <span className={`inline-block text-xs font-mono px-2 py-0.5 rounded-full ${scoreBg} ${scoreColor}`}>
                {importResult.recommendation}
              </span>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-very-muted font-mono text-xs">Reviews</span>
              <p className="text-text font-mono font-medium">
                {importResult.pipeline.reviews_imported.toLocaleString()}
              </p>
            </div>
            <div>
              <span className="text-very-muted font-mono text-xs">Issues</span>
              <p className="text-text font-mono font-medium">
                {Object.values(importResult.pipeline.issues).reduce((a, b) => a + b, 0)}
              </p>
            </div>
            <div>
              <span className="text-very-muted font-mono text-xs">Players</span>
              <p className="text-text font-mono font-medium">
                {importResult.pipeline.current_players?.toLocaleString() ?? "N/A"}
              </p>
            </div>
          </div>
        </div>
      )}

      {results.length > 0 && (
        <div className="mt-3 space-y-2">
          {results.map((r, i) => (
            <div
              key={r.steam_app_id}
              className="flex items-center gap-3 border border-border rounded-lg p-3 bg-surface card-hover"
            >
              {r.cover_url && (
                <img
                  src={r.cover_url}
                  alt={r.name}
                  className="w-14 h-20 object-cover rounded"
                />
              )}
              <div className="flex-1 min-w-0">
                <p className="font-sans text-sm font-medium text-text truncate">
                  {r.name}
                </p>
                <p className="text-very-muted font-mono text-[10px] mt-0.5">
                  {r.steam_app_id}
                  {r.price !== null && ` · $${(r.price / 100).toFixed(2)}`}
                </p>
              </div>
              <button
                onClick={() => importBySteamAppId(r, i)}
                disabled={importing === i}
                className="bg-surface border border-border rounded-lg px-4 py-2 text-xs font-sans font-medium text-text hover:bg-surface-raised hover:border-border-active transition-colors disabled:opacity-50"
              >
                {importing === i ? "Scanning..." : "Import"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
