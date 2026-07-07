export function ManifestCard({ step }: { step: { step_name: string; provider?: string } }) {
  return (
    <div>
      <strong>{step.step_name}</strong>
      {step.provider && <span> — {step.provider}</span>}
    </div>
  );
}
