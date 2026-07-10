const FEATURES = [
  {
    title: "Multi-provider pipeline",
    body: "Storyboard, animate, voiceover, score, and compose with concurrent fan-out.",
  },
  {
    title: "Provenance manifests",
    body: "SHA-256 per step, Object Lock on B2, and verify anytime.",
  },
  {
    title: "Fork and replay",
    body: "Swap providers and trace parent_run_id lineage across experiments.",
  },
  {
    title: "Your data, your account",
    body: "Sign in with Google. Briefs, runs, and library are scoped to you only.",
  },
];

export function FeatureGrid() {
  return (
    <section className="feature-grid">
      {FEATURES.map((feature) => (
        <div key={feature.title} className="card">
          <h3>{feature.title}</h3>
          <p>{feature.body}</p>
        </div>
      ))}
    </section>
  );
}
