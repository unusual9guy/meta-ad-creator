"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient, isSupabaseConfigured } from "@/lib/supabase/client";

export default function SignUpPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const router = useRouter();
  const supabase = isSupabaseConfigured ? createClient() : null;

  if (!isSupabaseConfigured) {
    return (
      <>
        <h1 className="text-xl font-semibold text-ink">Setup required</h1>
        <p className="mt-4 text-sm text-ink-muted">
          Sign in and sign up need Supabase. Copy <code className="rounded bg-surface-muted px-1 py-0.5 text-xs">.env.local.example</code> to{" "}
          <code className="rounded bg-surface-muted px-1 py-0.5 text-xs">.env.local</code> and set:
        </p>
        <ul className="mt-3 list-inside list-disc text-sm text-ink-muted">
          <li>NEXT_PUBLIC_SUPABASE_URL</li>
          <li>NEXT_PUBLIC_SUPABASE_ANON_KEY</li>
        </ul>
        <p className="mt-4 text-sm text-ink-muted">
          Get these from your project at{" "}
          <a href="https://supabase.com/dashboard" target="_blank" rel="noreferrer" className="text-brand hover:underline">
            supabase.com/dashboard
          </a>
          .
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
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    setLoading(true);
    const { error: signUpError } = await supabase!.auth.signUp({ email, password });
    setLoading(false);
    if (signUpError) {
      setError(signUpError.message);
      return;
    }
    setSuccess(true);
    router.push("/dashboard");
    router.refresh();
  }

  if (success) {
    return (
      <p className="text-center text-ink-muted">
        Check your email to confirm your account, or{" "}
        <Link href="/dashboard" className="text-brand hover:underline">
          go to dashboard
        </Link>
        .
      </p>
    );
  }

  return (
    <>
      <h1 className="text-xl font-semibold text-ink">Create an account</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Already have an account?{" "}
        <Link href="/sign-in" className="text-brand hover:underline">
          Sign in
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
            autoComplete="new-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-2 block w-full rounded-md border border-surface-border bg-white px-4 py-2.5 text-ink placeholder:text-ink-subtle focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand"
          />
        </div>
        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-ink">
            Confirm password
          </label>
          <input
            id="confirmPassword"
            type="password"
            autoComplete="new-password"
            required
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="mt-2 block w-full rounded-md border border-surface-border bg-white px-4 py-2.5 text-ink placeholder:text-ink-subtle focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-brand px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-dark disabled:opacity-60 transition-colors"
        >
          {loading ? "Creating account…" : "Create account"}
        </button>
      </form>
    </>
  );
}
