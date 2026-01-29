"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient, isSupabaseConfigured } from "@/lib/supabase/client";

export default function SignInPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const supabase = isSupabaseConfigured ? createClient() : null;

  if (!isSupabaseConfigured) {
    return (
      <>
        <h1 className="text-xl font-semibold text-ink">Setup required</h1>
        <p className="mt-4 text-sm text-ink-muted">
          Sign in needs Supabase. Copy <code className="rounded bg-surface-muted px-1 py-0.5 text-xs">.env.local.example</code> to{" "}
          <code className="rounded bg-surface-muted px-1 py-0.5 text-xs">.env.local</code> and set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY.
        </p>
        <Link href="/" className="mt-6 inline-block text-sm text-brand hover:underline">
          ← Back to home
        </Link>
      </>
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const { error: signInError } = await supabase!.auth.signInWithPassword({ email, password });
    setLoading(false);
    if (signInError) {
      setError(signInError.message);
      return;
    }
    router.push("/dashboard");
    router.refresh();
  }

  return (
    <>
      <h1 className="text-xl font-semibold text-ink">Sign in</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Don&apos;t have an account?{" "}
        <Link href="/sign-up" className="text-brand hover:underline">
          Sign up
        </Link>
      </p>
      <form onSubmit={handleSubmit} className="mt-8 space-y-6">
        {error && (
          <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
            {error}
          </div>
        )}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-ink">
            Email
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-2 block w-full rounded-md border border-surface-border bg-white px-4 py-2.5 text-ink placeholder:text-ink-subtle focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand"
          />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-ink">
            Password
          </label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-2 block w-full rounded-md border border-surface-border bg-white px-4 py-2.5 text-ink placeholder:text-ink-subtle focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand"
          />
          <p className="mt-2 text-right">
            <Link href="/forgot-password" className="text-sm text-brand hover:underline">
              Forgot password?
            </Link>
          </p>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-brand px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-dark disabled:opacity-60 transition-colors"
        >
          {loading ? "Signing in…" : "Sign in"}
        </button>
      </form>
    </>
  );
}
