"use client";

import { useEffect, useState } from "react";
import { getHealth } from "@/lib/api-client";

export function MockModeBadge() {
  const [mockMode, setMockMode] = useState<boolean | null>(null);

  useEffect(() => {
    getHealth()
      .then((h) => setMockMode(h.mock_mode))
      .catch(() => setMockMode(null));
  }, []);

  if (mockMode !== true) return null;

  return (
    <span
      className="badge badge-warning"
      style={{
        background: "rgba(245, 158, 11, 0.15)",
        borderColor: "rgba(245, 158, 11, 0.5)",
        color: "#fbbf24",
        fontWeight: 700,
      }}
      title="Pipeline is using mock/fixture data — not real provider output"
    >
      MOCK DATA
    </span>
  );
}
