import { apiFetch } from "@/lib/api";
import { SteamSearch } from "@/components/steam-search";

interface AdminStatus {
  games_count: number;
  reviews_count: number;
  health_scores_count: number;
  status: string;
}

export default async function AdminPage() {
  let status: AdminStatus = {
    games_count: 0,
    reviews_count: 0,
    health_scores_count: 0,
    status: "unknown",
  };
  try {
    status = await apiFetch("/admin/status");
  } catch {}

  return (
    <main className="min-h-screen">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <h1 className="font-display text-3xl italic text-text mb-8">admin</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
          {[
            { label: "Games", value: status.games_count, color: "text-cyan" },
            { label: "Reviews", value: status.reviews_count, color: "text-healthy" },
            { label: "Snapshots", value: status.health_scores_count, color: "text-playable" },
          ].map((card) => (
            <div key={card.label} className="border border-border rounded-lg p-5 bg-surface">
              <div className="flex items-center gap-2 mb-2">
                <div className={`w-2 h-2 rounded-full ${card.color.replace("text-", "bg-")}`} />
                <span className="text-xs font-mono text-muted uppercase tracking-wider">{card.label}</span>
              </div>
              <div className="font-mono text-2xl font-medium text-text">{card.value.toLocaleString()}</div>
            </div>
          ))}
        </div>

        <div className="border border-border rounded-lg p-5 bg-surface mb-8">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${status.status === "ok" ? "bg-healthy" : "bg-danger"}`} />
            <span className="text-sm text-muted">
              {status.status === "ok" ? "All systems operational" : "Issues detected"}
            </span>
          </div>
        </div>

        <SteamSearch />
      </div>
    </main>
  );
}
