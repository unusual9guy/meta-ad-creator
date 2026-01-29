import Link from "next/link";

export default function NewProjectPage() {
  return (
    <div className="mx-auto max-w-2xl">
      <Link
        href="/dashboard"
        className="text-sm text-ink-muted hover:text-ink transition-colors"
      >
        ← Back to projects
      </Link>
      <h1 className="mt-4 text-2xl font-semibold text-ink">New project</h1>
      <p className="mt-2 text-ink-muted">
        Project creation and the full ad workflow will be wired up when the backend API is ready.
      </p>
      <div className="mt-8 rounded-lg border border-surface-border bg-white p-8 text-center text-ink-muted">
        Upload image and run workflow (coming with Phase 2 backend).
      </div>
    </div>
  );
}
