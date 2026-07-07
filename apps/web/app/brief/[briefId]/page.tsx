export default function BriefPage({ params }: { params: { briefId: string } }) {
  return (
    <main>
      <h1>Brief {params.briefId}</h1>
      <p>Generation progress and variant picker</p>
    </main>
  );
}
