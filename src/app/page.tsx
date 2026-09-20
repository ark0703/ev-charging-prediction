import { PredictorApp } from "@/components/predictor-app";
import { loadBootstrapData } from "@/lib/api-server";

export const dynamic = "force-dynamic";

export default async function Home() {
  const bootstrap = await loadBootstrapData();

  return (
    <main className="min-h-full bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.12),_transparent_45%)]">
      <PredictorApp bootstrap={bootstrap} />
    </main>
  );
}
