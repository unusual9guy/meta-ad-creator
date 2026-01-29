import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-surface-border bg-surface">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
          <span className="text-lg font-semibold text-ink">Meta Ad Creator</span>
          <nav className="flex items-center gap-6">
            <Link
              href="/sign-in"
              className="text-sm text-ink-muted hover:text-ink transition-colors"
            >
              Sign in
            </Link>
            <Link
              href="/sign-up"
              className="rounded-md bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark transition-colors"
            >
              Get started
            </Link>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <section className="mx-auto max-w-4xl px-4 py-24 text-center sm:px-6">
          <h1 className="text-4xl font-semibold tracking-tight text-ink sm:text-5xl">
            Professional Meta ad creatives from your product images
          </h1>
          <p className="mt-6 text-lg text-ink-muted max-w-2xl mx-auto">
            Upload a product image, add a few details, and get brand-aware,
            photorealistic ad creatives—no design skills required.
          </p>
          <div className="mt-10 flex flex-wrap justify-center gap-4">
            <Link
              href="/sign-up"
              className="rounded-md bg-brand px-6 py-3 text-base font-medium text-white hover:bg-brand-dark transition-colors"
            >
              Create your first ad
            </Link>
            <Link
              href="/sign-in"
              className="rounded-md border border-surface-border bg-surface px-6 py-3 text-base font-medium text-ink hover:bg-surface-muted transition-colors"
            >
              Sign in
            </Link>
          </div>
        </section>

        <section className="border-t border-surface-border bg-surface-muted/50 py-24">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <h2 className="text-center text-2xl font-semibold text-ink">
              How it works
            </h2>
            <div className="mt-16 grid gap-12 sm:grid-cols-3">
              <div className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full border border-surface-border text-ink-muted text-lg font-semibold">
                  1
                </div>
                <h3 className="mt-4 text-lg font-medium text-ink">Upload & describe</h3>
                <p className="mt-2 text-sm text-ink-muted">
                  Upload your product image and add name, audience, and optional promotion.
                </p>
              </div>
              <div className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full border border-surface-border text-ink-muted text-lg font-semibold">
                  2
                </div>
                <h3 className="mt-4 text-lg font-medium text-ink">AI does the rest</h3>
                <p className="mt-2 text-sm text-ink-muted">
                  We analyze the product, remove the background, and generate a tailored ad prompt.
                </p>
              </div>
              <div className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full border border-surface-border text-ink-muted text-lg font-semibold">
                  3
                </div>
                <h3 className="mt-4 text-lg font-medium text-ink">Download your creative</h3>
                <p className="mt-2 text-sm text-ink-muted">
                  Get a 1:1 Meta-ready creative with typography and styling that fits your brand.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-surface-border py-8">
        <div className="mx-auto max-w-6xl px-4 text-center text-sm text-ink-subtle sm:px-6">
          Meta Ad Creator — AI-powered ad creatives
        </div>
      </footer>
    </div>
  );
}
