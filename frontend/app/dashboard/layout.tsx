"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient, isSupabaseConfigured } from "@/lib/supabase/client";
import { useEffect, useState } from "react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [user, setUser] = useState<{ email?: string } | null>(null);
  const router = useRouter();
  useEffect(() => {
    if (!isSupabaseConfigured) {
      setUser(null);
      router.push("/sign-in");
      return;
    }
    const supabase = createClient();
    supabase.auth.getUser().then(({ data: { user: u } }) => {
      setUser(u ?? null);
      if (!u) router.push("/sign-in");
    });
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
      if (!session) router.push("/sign-in");
    });
    return () => subscription.unsubscribe();
  }, [router]);

  const supabase = isSupabaseConfigured ? createClient() : null;

  async function handleSignOut() {
    if (supabase) await supabase.auth.signOut();
    router.push("/");
    router.refresh();
  }

  if (!isSupabaseConfigured) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-surface px-4">
        <p className="text-center font-medium text-ink">Setup required</p>
        <p className="mt-2 max-w-md text-center text-sm text-ink-muted">
          Add NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY to .env.local. See frontend/.env.local.example.
        </p>
        <Link href="/" className="mt-6 text-sm text-brand hover:underline">
          ← Back to home
        </Link>
      </div>
    );
  }

  if (user === null) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-surface">
        <p className="text-ink-muted">Loading…</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-surface">
      <header className="border-b border-surface-border bg-white">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
          <Link href="/dashboard" className="text-lg font-semibold text-ink hover:text-brand transition-colors">
            Meta Ad Creator
          </Link>
          <nav className="flex items-center gap-6">
            <span className="text-sm text-ink-muted">{user?.email}</span>
            <button
              type="button"
              onClick={handleSignOut}
              className="text-sm text-ink-muted hover:text-ink transition-colors"
            >
              Sign out
            </button>
          </nav>
        </div>
      </header>
      <main className="flex-1 px-4 py-8 sm:px-6">
        {children}
      </main>
    </div>
  );
}
