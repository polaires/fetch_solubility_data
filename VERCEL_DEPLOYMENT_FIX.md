# Vercel Deployment Fix for 404 Error

## Problem
Getting `404: NOT_FOUND` error because Vercel is deploying from repository root instead of `web-interface/` directory.

## Solution Options

### Option 1: Configure in Vercel Dashboard (Recommended)

1. **Go to your Vercel project**
   - Visit https://vercel.com/dashboard
   - Select your project

2. **Update Settings**
   - Go to **Settings** → **General**
   - Find **Root Directory** section
   - Click **Edit**
   - Set to: `web-interface`
   - Click **Save**

3. **Redeploy**
   - Go to **Deployments**
   - Click **⋯** on latest deployment
   - Click **Redeploy**
   - ✅ Should work now!

### Option 2: Deploy from web-interface Directory Directly

```bash
# Navigate to web-interface
cd web-interface

# Deploy from here
vercel

# Follow prompts - Vercel will auto-detect Next.js
```

This creates a separate Vercel project just for the web interface.

### Option 3: Use Vercel CLI with Root Directory Flag

```bash
# From repository root
vercel --cwd web-interface
```

## Verify Configuration

After deploying, you should see:
- ✅ Homepage with table browser
- ✅ Search functionality
- ✅ Individual table views
- ✅ No 404 errors

## Troubleshooting

### Still getting 404?

**Check build logs:**
1. Go to Vercel Dashboard → Deployments
2. Click on your deployment
3. Check "Building" and "Function Logs"
4. Look for errors

**Common issues:**
- Root directory not set correctly
- Build failing (check logs)
- API routes not working (check CSV data path)

### API routes returning errors?

The API routes expect data in `../output/02_cleaned/`. On Vercel, this won't work because:
- Vercel deployments are serverless
- File system is read-only
- Parent directories aren't accessible

**Solution for production:**
You need to either:
1. Copy CSV files into `web-interface/public/data/`
2. Or migrate to Postgres (already prepared)

### Quick Fix: Copy Data Into web-interface

```bash
# From repository root
mkdir -p web-interface/public/data
cp output/02_cleaned/*.csv web-interface/public/data/

# Update API to read from public/data
# Then redeploy
```

## Alternative: Local Development Only

If you just want to test locally without Vercel deployment:

```bash
cd web-interface
npm run dev
# Access at http://localhost:3000
```

This works perfectly because it can access `../output/02_cleaned/`.

## Best Solution: Postgres Migration

For production deployment, migrate to Vercel Postgres:

1. **Setup Postgres**
   ```bash
   # In Vercel Dashboard
   Storage → Create → Postgres
   ```

2. **Import Data**
   ```bash
   # Run migration script (to be created)
   node scripts/import-to-postgres.js
   ```

3. **Update API routes**
   - Already prepared in `lib/db.ts`
   - Just uncomment Postgres queries

This gives you:
- ✅ Proper production deployment
- ✅ Fast queries
- ✅ Scalable storage
- ✅ No file system dependencies

---

**TL;DR:** Set Root Directory to `web-interface` in Vercel project settings, then redeploy.
