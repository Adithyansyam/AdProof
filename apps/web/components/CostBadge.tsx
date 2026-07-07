export function CostBadge({ provider, cost }: { provider: string; cost: string }) {
  return (
    <span>
      {provider} · ${cost}
    </span>
  );
}
