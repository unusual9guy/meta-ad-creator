import Link from "next/link";

export default function DashboardPage() {
  return (
    <div className="mx-auto max-w-6xl">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-ink">Projects</h1>
      </div>
      <div className="mt-12 rounded-lg border border-surface-border bg-white p-12 text-center">
        <p className="text-ink-muted">You don&apos;t have any projects yet.</p>
        <p className="mt-2 text-sm text-ink-subtle">
          Create your first ad to get started.
        </p>
        <Link
          href="/dashboard/new"
          className="mt-6 inline-block rounded-md bg-brand px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-dark transition-colors"
        >
          Create your first ad
        </Link>
      </div>
    </div>
  );
}
