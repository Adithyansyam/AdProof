export default function RunPage({ params }: { params: { runId: string } }) {
  return (
    <main>
      <h1>Provenance — Run {params.runId}</h1>
      <p>Step timeline, verify button, fork UI — see docs/frontend-spec.md</p>
    </main>
  );
}
