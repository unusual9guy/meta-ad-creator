import Link from "next/link";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-surface px-4 py-12">
      <Link href="/" className="mb-8 text-lg font-semibold text-ink hover:text-brand transition-colors">
        Meta Ad Creator
      </Link>
      <div className="w-full max-w-md rounded-lg border border-surface-border bg-white p-8 shadow-sm">
        {children}
      </div>
    </div>
  );
}
