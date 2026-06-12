"use client";

import { useState } from "react";

interface RescoreResult {
  score: number;
  recommendation: string;
}

export function RescoreButton({ gameId }: { gameId: number }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RescoreResult | null>(null);

  async function rescore() {
    setLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/games/${gameId}/score`,
        { method: "POST" }
      );
      const data = await res.json();
      setResult(data);
    } catch {
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <button
        onClick={rescore}
        disabled={loading}
        className="bg-surface border border-border rounded-lg px-4 py-2 text-sm font-sans font-medium text-text hover:bg-surface-raised hover:border-border-active transition-colors disabled:opacity-50"
      >
        {loading ? "Recalculating..." : "Rescore Now"}
      </button>
      {result && (
        <div className="mt-3 text-sm">
          <span className="font-mono text-muted">
            New score: <span className="text-text">{result.score}</span> · {result.recommendation}
          </span>
          <p className="text-very-muted font-mono text-xs mt-1">
            Refresh the page to see updated data.
          </p>
        </div>
      )}
    </div>
  );
}
