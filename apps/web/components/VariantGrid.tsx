import Link from "next/link";
import type { Variant } from "@/lib/types";
import { CostBadge } from "./CostBadge";

export function VariantGrid({
  variants,
  runId,
}: {
  variants: Variant[];
  runId: string;
}) {
  return (
    <div className="grid grid-2">
      {variants.map((v) => (
        <div key={v.id} className="card">
          {v.thumbnail_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={v.thumbnail_url}
              alt="Variant thumbnail"
              style={{ width: "100%", borderRadius: 8, marginBottom: "0.75rem" }}
            />
          ) : (
            <div
              style={{
                height: 160,
                background: "#1f2433",
                borderRadius: 8,
                marginBottom: "0.75rem",
                display: "grid",
                placeItems: "center",
              }}
            >
              Preview
            </div>
          )}
          {v.provider_summary && (
            <CostBadge provider={v.provider_summary} cost="—" />
          )}
          <p style={{ fontSize: "0.8rem", wordBreak: "break-all" }}>
            SHA-256: {v.sha256_hash.slice(0, 16)}...
          </p>
          <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.75rem" }}>
            <Link href={`/run/${runId}`} className="btn btn-secondary">
              Provenance
            </Link>
            {v.asset_url && (
              <a href={v.asset_url} className="btn" target="_blank" rel="noreferrer">
                Download
              </a>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
