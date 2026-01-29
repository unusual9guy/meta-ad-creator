"use client";

import { useState } from "react";
import Link from "next/link";
import { createClient, isSupabaseConfigured } from "@/lib/supabase/client";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const supabase = isSupabaseConfigured ? createClient() : null;

  if (!isSupabaseConfigured) {
    return (
      <>
        <h1 className="text-xl font-semibold text-ink">Setup required</h1>
        <p className="mt-4 text-sm text-ink-muted">
          Add NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY to .env.local. See .env.local.example.
        </p>
        <Link href="/sign-in" className="mt-6 inline-block text-sm text-brand hover:underline">
          ← Back to sign in
        </Link>
      </>
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const { error: resetError } = await supabase!.auth.resetPasswordForEmail(email, {
      redirectTo: `${typeof window !== "undefined" ? window.location.origin : ""}/sign-in`,
    });
    setLoading(false);
    if (resetError) {
      setError(resetError.message);
      return;
    }
    setSent(true);
  }

  if (sent) {
    return (
      <>
        <h1 className="text-xl font-semibold text-ink">Check your email</h1>
        <p className="mt-4 text-sm text-ink-muted">
          If an account exists for {email}, we&apos;ve sent a link to reset your password.
        </p>
        <Link
          href="/sign-in"
          className="mt-6 inline-block text-sm text-brand hover:underline"
        >
          Back to sign in
        </Link>
      </>
    );
  }

  return (
    <>
      <h1 className="text-xl font-semibold text-ink">Forgot password</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Enter your email and we&apos;ll send you a link to reset your password.
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
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-brand px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-dark disabled:opacity-60 transition-colors"
        >
          {loading ? "Sending…" : "Send reset link"}
        </button>
      </form>
      <p className="mt-6 text-center">
        <Link href="/sign-in" className="text-sm text-ink-muted hover:text-ink transition-colors">
          Back to sign in
        </Link>
      </p>
    </>
  );
}
