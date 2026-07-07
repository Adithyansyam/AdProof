import type { RunStep } from "@/lib/types";

export function ManifestCard({ step }: { step: RunStep }) {
  return (
    <div className="card" style={{ padding: "0.75rem", background: "#101522" }}>
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
        <span className="badge">{step.provider || "—"}</span>
        <span className="badge">{step.model || step.step_name}</span>
        <span className={`badge ${step.status === "succeeded" ? "badge-success" : step.fallback_triggered ? "badge-warning" : ""}`}>
          {step.fallback_triggered ? "fallback used" : step.status}
        </span>
        {step.latency_ms != null && (
          <span className="badge">{step.latency_ms}ms</span>
        )}
      </div>
      {step.manifest_key && (
        <p style={{ margin: "0.5rem 0 0", fontSize: "0.75rem", wordBreak: "break-all" }}>
          manifest: {step.manifest_key}
        </p>
      )}
    </div>
  );
}
