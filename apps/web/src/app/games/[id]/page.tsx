import { apiFetch } from "@/lib/api";
import { notFound } from "next/navigation";
import type { Game } from "@game-health/types";
import { HealthGauge } from "@/components/health-gauge";
import { RescoreButton } from "@/components/rescore-button";

interface HealthSnapshot {
  score: number;
  sentiment: number;
  stability: number;
  retention: number;
  recommendation: string;
  created_at: string;
}

interface IssueDetail {
  type: string;
  count: number;
  summaries: string[];
}

interface IssueData {
  game_id: number;
  total_issues: number;
  issues: Record<string, number>;
  details: IssueDetail[];
}

function getScoreColor(score: number): string {
  if (score >= 80) return "text-healthy";
  if (score >= 60) return "text-playable";
  if (score >= 40) return "text-warning";
  return "text-danger";
}

function getScoreBorder(score: number): string {
  if (score >= 80) return "border-healthy/20";
  if (score >= 60) return "border-playable/20";
  if (score >= 40) return "border-warning/20";
  return "border-danger/20";
}

export default async function GameDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const id = Number(params.id);
  if (isNaN(id)) notFound();

  let game: Game & {
    health_score?: number;
    recommendation?: string;
    sentiment?: number;
    stability?: number;
    retention_score?: number;
  };
  try {
    game = await apiFetch(`/games/${id}`);
  } catch {
    notFound();
  }

  if ("error" in game) notFound();

  let healthHistory: HealthSnapshot[] = [];
  try {
    healthHistory = await apiFetch(`/games/${id}/health`);
  } catch {}

  let issues: IssueData = { game_id: id, total_issues: 0, issues: {}, details: [] };
  try {
    issues = await apiFetch(`/games/${id}/issues`);
  } catch {}

  let recommendation: { recommendation: string; score: number } = {
    recommendation: "NO DATA",
    score: 0,
  };
  try {
    recommendation = await apiFetch(`/games/${id}/recommendation`);
  } catch {}

  const latestScore = healthHistory[healthHistory.length - 1];
  const score = game.health_score ?? latestScore?.score ?? 0;
  const rec = game.recommendation ?? recommendation.recommendation;
  const scoreColor = getScoreColor(score);
  const scoreBorder = getScoreBorder(score);

  const trend =
    healthHistory.length >= 2
      ? healthHistory[healthHistory.length - 1].score - healthHistory[0].score
      : 0;

  const issueDetails = issues.details ?? [];

  return (
    <main className="min-h-screen">
      {/* Hero */}
      <div className="relative">
        {game.cover_url && (
          <div className="absolute inset-0 h-80 overflow-hidden">
            <img
              src={game.cover_url}
              alt={game.name}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-b from-[#090909]/60 via-[#090909]/40 to-[#090909]" />
          </div>
        )}
        <div className="relative max-w-6xl mx-auto px-6 pt-8 pb-12">
          <a href="/" className="text-very-muted text-sm font-mono hover:text-text transition-colors">
            ← Back
          </a>
          <div className="mt-8 flex flex-col md:flex-row items-start gap-8">
            <div className="flex-1">
              <h1 className="font-display text-4xl italic text-text mb-2">
                {game.name}
              </h1>
              <p className="text-muted font-mono text-sm">
                {game.developer && game.developer}
                {game.publisher && ` · ${game.publisher}`}
                {game.release_date && ` · ${game.release_date}`}
              </p>
              {game.platforms && (
                <p className="text-very-muted font-mono text-xs mt-1">
                  {game.platforms}
                </p>
              )}
              {game.genre && (
                <p className="text-very-muted font-mono text-xs">
                  {game.genre}
                </p>
              )}
            </div>
            <div className="flex-shrink-0 flex flex-col items-center gap-3">
              <HealthGauge score={score} recommendation={rec} steamAppId={game.steam_app_id} />
              {game.steam_deck_status && (
                <span className={`font-pixel text-[9px] tracking-tighter px-2 py-1 rounded ${
                  game.steam_deck_status === "verified"
                    ? "bg-healthy/10 text-healthy border border-healthy/30"
                    : game.steam_deck_status === "playable"
                      ? "bg-playable/10 text-playable border border-playable/30"
                      : "bg-warning/10 text-warning border border-warning/30"
                }`}>
                  DECK {game.steam_deck_status.toUpperCase()}
                </span>
              )}
              {trend !== 0 && (
                <div className={`text-sm font-mono ${trend > 0 ? "text-healthy" : "text-danger"}`}>
                  {trend > 0 ? "+" : ""}{trend} pts
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 pb-16">
        {/* Vitals */}
        <div className="section-divider mb-12" />
        <section className="mb-12">
          <h2 className="font-sans text-sm font-semibold text-muted uppercase tracking-wider mb-6">
            Vitals
          </h2>
          <p className="text-very-muted text-xs font-mono mb-6">
            Health Score = Sentiment 45% + Stability 25% + Retention 20% + Deck 10%
          </p>
          <div className="space-y-5">
            {[
              { label: "Sentiment", value: game.sentiment ?? latestScore?.sentiment ?? 0, weight: 50 },
              { label: "Stability", value: game.stability ?? latestScore?.stability ?? 0, weight: 30 },
              { label: "Retention", value: game.retention_score ?? latestScore?.retention ?? 0, weight: 20 },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex justify-between items-baseline mb-2">
                  <span className="text-sm text-text font-medium">{item.label}</span>
                  <span className="font-mono text-sm text-muted">
                    {item.value} <span className="text-very-muted">({item.weight}%)</span>
                  </span>
                </div>
                <div className="w-full bg-surface rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full ${scoreColor.replace("text-", "bg-")}`}
                    style={{ width: `${item.value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
          <div className="mt-8">
            <RescoreButton gameId={game.id} />
          </div>
        </section>

        {/* Incident Evidence */}
        <div className="section-divider mb-12" />
        <section className="mb-12">
          <h2 className="font-sans text-sm font-semibold text-muted uppercase tracking-wider mb-6">
            Incident Evidence
          </h2>
          {issueDetails.length === 0 ? (
            <p className="text-very-muted font-mono text-sm">No incidents detected in reviews.</p>
          ) : (
            <div className="space-y-6">
              {issueDetails.map((detail) => (
                <div key={detail.type}>
                  <div className="flex items-center gap-3 mb-3">
                    <span className="font-mono text-xs text-muted uppercase tracking-wider">
                      {detail.type.replace("_", " ")}
                    </span>
                    <span className={`text-xs font-mono px-2 py-0.5 rounded-full ${scoreColor.replace("text-", "bg-")}/10 ${scoreColor}`}>
                      {detail.count}
                    </span>
                  </div>
                  {detail.summaries.length > 0 && (
                    <div className="space-y-2 ml-4 border-l-2 border-border pl-4">
                      {detail.summaries.slice(0, 3).map((summary, i) => (
                        <p key={i} className="text-muted text-sm leading-relaxed">
                          {summary}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Timeline */}
        {healthHistory.length > 1 && (
          <>
            <div className="section-divider mb-12" />
            <section className="mb-12">
              <h2 className="font-sans text-sm font-semibold text-muted uppercase tracking-wider mb-6">
                Score History
              </h2>
              <div className="flex items-end gap-px h-28">
                {healthHistory.map((snapshot, i) => {
                  const h = snapshot.score;
                  const color =
                    snapshot.score >= 80
                      ? "bg-healthy"
                      : snapshot.score >= 60
                        ? "bg-playable"
                        : snapshot.score >= 40
                          ? "bg-warning"
                          : "bg-danger";
                  return (
                    <div key={i} className="flex flex-col items-center flex-1 group">
                      <div className="opacity-0 group-hover:opacity-100 transition-opacity text-[10px] text-muted font-mono mb-1">
                        {snapshot.score}
                      </div>
                      <div
                        className={`w-full rounded-t ${color} opacity-70 group-hover:opacity-100 transition-opacity`}
                        style={{ height: `${h}%` }}
                      />
                    </div>
                  );
                })}
              </div>
              <div className="flex justify-between text-[10px] text-very-muted font-mono mt-2">
                <span>{new Date(healthHistory[0].created_at).toLocaleDateString()}</span>
                <span>{new Date(healthHistory[healthHistory.length - 1].created_at).toLocaleDateString()}</span>
              </div>
            </section>
          </>
        )}
      </div>
    </main>
  );
}
