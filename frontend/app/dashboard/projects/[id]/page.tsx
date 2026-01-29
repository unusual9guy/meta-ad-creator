import Link from "next/link";

export default function ProjectDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const { id } = params;
  return (
    <div className="mx-auto max-w-4xl">
      <Link
        href="/dashboard"
        className="text-sm text-ink-muted hover:text-ink transition-colors"
      >
        ← Back to projects
      </Link>
      <h1 className="mt-4 text-2xl font-semibold text-ink">Project</h1>
      <p className="mt-1 text-sm text-ink-muted">ID: {id}</p>
      <div className="mt-8 rounded-lg border border-surface-border bg-white p-8 text-center text-ink-muted">
        Stepper and workflow actions will appear here when the backend is connected.
      </div>
    </div>
  );
}
