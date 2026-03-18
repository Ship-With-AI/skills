# Stack Guides

Provider-specific deployment instructions. The agent reads the relevant section based on what `detect_stack.py` reports.

---

## Hosting

### Vercel

**Best for:** Next.js, Astro, SvelteKit, Remix, static sites.

**CLI Deploy:**
```bash
npm i -g vercel
vercel login          # Browser auth — user must do this manually
vercel link           # Links to project (creates one if new)
vercel --prod         # Production deploy
```

**vercel.json (Next.js):**
```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "nextjs"
}
```

**vercel.json (Astro):**
```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "astro"
}
```

**vercel.json (SvelteKit):**
```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "sveltekit"
}
```

**Environment Variables:**
```bash
vercel env add VARIABLE_NAME production      # Interactive prompt
vercel env add VARIABLE_NAME production < file.txt  # From file
vercel env ls                                 # List all
vercel env rm VARIABLE_NAME production        # Remove
```

**Custom Domain:**
```bash
vercel domains add yourdomain.com
# Then set DNS: CNAME → cname.vercel-dns.com
```

**Common Issues:**
- Build fails with "Module not found" → missing dependency in package.json (check devDependencies vs dependencies)
- 500 error on API routes → missing environment variable (check vercel env ls)
- Middleware redirect loop → check middleware.ts matcher config

---

### Railway

**Best for:** Backend-heavy apps, monorepos, apps needing background workers, WebSocket support.

**CLI Deploy:**
```bash
npm i -g @railway/cli
railway login         # Browser auth — user must do this manually
railway init          # Creates project
railway link          # Links to project
railway up            # Deploy
```

**Environment Variables:**
```bash
railway variables set KEY=value
railway variables set KEY=value KEY2=value2   # Multiple
railway variables                              # List all
```

**Custom Domain:**
```bash
railway domain        # Generates *.up.railway.app URL
# Custom: Railway dashboard → Settings → Domains → Add custom domain
# Set DNS: CNAME → [provided by Railway]
```

**Common Issues:**
- Build fails → check Nixpacks detection. Add `nixpacks.toml` if needed.
- Port issues → Railway sets PORT env var. App must listen on process.env.PORT.

---

## Database

### Supabase

**CLI Setup:**
```bash
npm i -g supabase
supabase login                                # Browser auth
supabase link --project-ref YOUR_PROJECT_REF  # Link to production
supabase db push                              # Apply migrations
```

**Get project ref:** Supabase dashboard → Project Settings → General → Reference ID

**Environment Variables Needed:**
```
NEXT_PUBLIC_SUPABASE_URL=https://[ref].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[anon key from dashboard → API]
SUPABASE_SERVICE_ROLE_KEY=[service role key — only for server-side]
```

**Verify connection:**
```bash
supabase db dump --schema public | head -20   # Check tables exist
```

---

### Neon

**No CLI needed for basic setup.** Get connection string from Neon dashboard.

**Environment Variables Needed:**
```
DATABASE_URL=postgresql://[user]:[password]@[host]/[dbname]?sslmode=require
```

**Apply migrations:**
- Prisma: `npx prisma migrate deploy`
- Drizzle: `npx drizzle-kit push`

---

## Auth

### Clerk

**Production keys are different from development keys.**

Get production keys: Clerk dashboard → Your app → API Keys → Production

**Environment Variables Needed:**
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_SECRET_KEY=sk_live_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
```

---

### Auth.js / NextAuth

**Generate production secret:**
```bash
openssl rand -base64 32
```

**Environment Variables Needed:**
```
NEXTAUTH_SECRET=[generated secret]
NEXTAUTH_URL=https://yourdomain.com
```

**OAuth providers:** Update redirect URLs in provider developer console to include production domain.

---

### Supabase Auth

Uses the same Supabase client — no additional setup beyond Step 2. Verify:
- Auth settings in Supabase dashboard → Authentication → URL Configuration
- Set "Site URL" to production URL
- Add production URL to "Redirect URLs"

---

## Payments

### Stripe

**Setup requires Stripe dashboard — cannot be automated.**

1. Create account at stripe.com (if new)
2. Get API keys: Stripe dashboard → Developers → API keys
3. For test mode: use `sk_test_` and `pk_test_` keys
4. For live mode: activate account, use `sk_live_` and `pk_live_` keys

**Environment Variables Needed:**
```
STRIPE_SECRET_KEY=sk_live_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...  (if using webhooks)
```

**Webhook setup:**
```bash
# For local testing:
stripe listen --forward-to localhost:3000/api/webhooks/stripe

# For production: Stripe dashboard → Developers → Webhooks → Add endpoint
# URL: https://yourdomain.com/api/webhooks/stripe
# Events: checkout.session.completed, customer.subscription.updated (adjust to your needs)
```

---

### LemonSqueezy

1. Create account at lemonsqueezy.com
2. Get API key: Settings → API
3. Create a store and product

**Environment Variables Needed:**
```
LEMONSQUEEZY_API_KEY=[api key]
LEMONSQUEEZY_STORE_ID=[store id]
LEMONSQUEEZY_WEBHOOK_SECRET=[webhook secret]
```
