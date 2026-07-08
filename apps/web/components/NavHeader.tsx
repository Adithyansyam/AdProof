"use client";

import Link from "next/link";
import { MockModeBadge } from "./MockModeBadge";

export function NavHeader() {
  return (
    <header style={{ borderBottom: "1px solid var(--border)" }}>
      <div
        style={{
          maxWidth: 1100,
          margin: "0 auto",
          padding: "1rem 1.5rem",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "1rem",
        }}
      >
        <nav className="nav" style={{ margin: 0, padding: 0, border: "none" }}>
          <Link href="/"><strong>AdProof</strong></Link>
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/library">Library</Link>
        </nav>
        <MockModeBadge />
      </div>
    </header>
  );
}
