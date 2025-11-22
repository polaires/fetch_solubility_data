# Web Interface Guide

## 📱 Solubility Data Viewer - Complete Guide

A beautiful, modern web interface for examining and browsing your extracted solubility data.

---

## 🎯 What You Can Do

### Browse All Tables
- View all 338 extracted tables organized by PDF part
- See table metadata (rows, columns, size)
- Quick stats dashboard showing totals

### Search & Filter
- Search by table filename
- Filter by PDF part (Part1-Part7)
- Real-time results

### View Table Data
- Click any table to see full contents
- Pagination (50 rows per page)
- Search within individual tables
- Sticky headers for easy navigation
- Responsive design works on mobile/tablet/desktop

---

## 🚀 Getting Started

### Option 1: Local Development (Fastest)

```bash
# Navigate to web interface
cd web-interface

# Install dependencies (only needed once)
npm install

# Start development server
npm run dev

# Open browser to http://localhost:3000
```

That's it! The interface will automatically read from `../output/02_cleaned/` directory.

### Option 2: Deploy to Vercel (Production)

1. **Install Vercel CLI** (one-time setup)
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   cd web-interface
   vercel
   ```

3. **Follow prompts:**
   - Link to your Vercel account
   - Set project name
   - Deploy!

4. **Get your URL:**
   ```
   ✅ Production: https://your-project.vercel.app
   ```

---

## 📸 Interface Overview

### Home Page (Table Browser)

```
┌─────────────────────────────────────────────────────────────┐
│  Solubility Data Viewer                                      │
│  Browse and examine extracted solubility data from SDS-31    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [338 Total Tables]  [7 PDF Parts]  [338 Filtered Results]  │
│                                                              │
│  [Search: ____________]  [Filter by Part: All ▼]            │
│                                                              │
│  ┌─ Part1 (40 tables) ──────────────────────────────────┐  │
│  │  Table 001 → SDS-31_Part1_table_001.csv  [10×5]   >  │  │
│  │  Table 002 → SDS-31_Part1_table_002.csv  [15×8]   >  │  │
│  │  Table 003 → SDS-31_Part1_table_003.csv  [20×6]   >  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─ Part2 (62 tables) ──────────────────────────────────┐  │
│  │  Table 001 → SDS-31_Part2_table_001.csv  [12×7]   >  │  │
│  │  ...                                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Table Detail Page

```
┌─────────────────────────────────────────────────────────────┐
│  ← Back to Tables                                            │
│  Part1 - Table 001                         45 rows × 8 cols │
│  SDS-31_Part1_table_001.csv                         2.1 KB  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Search in table: ____________]     Showing 1-45 of 45     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ # │ Col1   │ Col2   │ Col3   │ Col4   │ ...         │  │
│  ├───┼────────┼────────┼────────┼────────┼────────────┤  │
│  │ 1 │ 10.33  │ 6.36   │ 52.07  │ 14.00  │ ...         │  │
│  │ 2 │ 7.39   │ 4.48   │ 53.66  │ 14.22  │ ...         │  │
│  │ 3 │ 5.10   │ 3.09   │ 55.39  │ 14.64  │ ...         │  │
│  │...│        │        │        │        │             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  [◄ Previous]    [1] 2 3 4 5    [Next ►]                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Usage Examples

### Example 1: Find Specific Table

```
1. Open http://localhost:3000
2. In search box, type: "Part2_table_046"
3. Click on the result
4. View the full table data
```

### Example 2: Browse All Part1 Tables

```
1. Open home page
2. Select "Part1" from filter dropdown
3. See only Part1 tables (40 tables)
4. Click any to view
```

### Example 3: Search Within a Table

```
1. Open any table (e.g., Part1 Table 033)
2. Use "Search in table" box
3. Type: "0.026"
4. See all rows containing that value
```

### Example 4: Export Table Data

```
Currently viewing table →
  1. Copy data from browser
  2. Or use browser "Save As" to get HTML
  3. Future: Direct CSV/JSON export coming!
```

---

## 🎨 Features in Detail

### Smart Search
- Searches filenames in real-time
- Case-insensitive
- Instant results
- No page reload needed

### Filtering
- Filter by PDF part (Part1-7)
- Combine with search
- Maintains your search term

### Pagination
- 50 rows per page (configurable)
- Smart page controls
- Shows current position
- Keyboard navigation ready

### Responsive Design
- Works on desktop (1920px+)
- Works on tablets (768px+)
- Works on mobile (320px+)
- Touch-friendly on mobile

### Performance
- Fast loading (~500ms initial)
- Cached API responses
- Smooth scrolling
- No lag with large tables

---

## 🛠️ Customization

### Change Rows Per Page

Edit `web-interface/app/table/[filename]/page.tsx`:

```typescript
const rowsPerPage = 50  // Change to 25, 100, etc.
```

### Change Data Source

Edit `web-interface/app/api/tables/route.ts`:

```typescript
const dataDir = path.join(process.cwd(), '..', 'output', '02_cleaned')
// Change to '01_extracted' for raw data
// Or '04_database' for database-ready files
```

### Add Custom Styling

Edit `web-interface/app/globals.css`:

```css
/* Add your custom styles here */
.custom-header {
  background: linear-gradient(to right, #667eea 0%, #764ba2 100%);
}
```

---

## 🚀 Deploying to Production

### Vercel Deployment (Recommended)

**Why Vercel?**
- Free tier available
- Automatic HTTPS
- Global CDN
- Zero configuration
- Git integration

**Steps:**

1. **Push to GitHub**
   ```bash
   git add web-interface/
   git commit -m "Add web interface"
   git push
   ```

2. **Go to vercel.com**
   - Sign in with GitHub
   - Click "New Project"
   - Import your repository

3. **Configure**
   - Root Directory: `web-interface`
   - Framework Preset: Next.js
   - Deploy!

4. **Access**
   ```
   Your site is live at:
   https://your-project.vercel.app
   ```

### Environment Variables (Optional)

For future Postgres integration:

```bash
# In Vercel dashboard
Settings → Environment Variables

DATABASE_URL = postgres://...
```

---

## 🗄️ Future: Migrating to Postgres

**When to migrate:**
- You have >1000 tables
- You need complex queries
- You want API access
- You need better performance

**How to migrate:**

1. **Set up Vercel Postgres**
   ```bash
   # In Vercel dashboard
   Storage → Create → Postgres
   ```

2. **Run migration**
   ```bash
   # Import schema
   psql $DATABASE_URL -f lib/schema.sql
   ```

3. **Import CSV data**
   ```bash
   # Use migration script (to be created)
   npm run migrate-csv-to-postgres
   ```

4. **Update API routes**
   - Swap CSV reading with Postgres queries
   - Already prepared in `lib/db.ts`

---

## 🐛 Troubleshooting

### Issue: "Data directory not found"

**Cause:** API can't find CSV files

**Solution:**
```bash
# Check data exists
ls ../output/02_cleaned/

# If not, run extraction first
cd ..
python pipeline.py --all
```

### Issue: "Build failed" in Vercel

**Cause:** Dependencies or build errors

**Solution:**
```bash
# Test build locally first
cd web-interface
npm run build

# Fix any errors, then redeploy
```

### Issue: Tables not showing

**Cause:** API route errors

**Solution:**
```bash
# Check browser console (F12)
# Look for error messages
# Check API response at: /api/tables
```

### Issue: Slow performance

**Cause:** Large tables

**Solution:**
- Reduce `rowsPerPage` to 25
- Consider Postgres migration
- Enable API caching

---

## 📊 Performance Tips

### For Large Datasets

```bash
# 1. Use pagination (already enabled)
# 2. Implement server-side filtering
# 3. Add API caching
# 4. Migrate to Postgres
```

### For Fast Loading

```bash
# 1. Deploy to Vercel (CDN)
# 2. Enable static generation where possible
# 3. Optimize images (if any)
# 4. Use lazy loading for tables
```

---

## 🎯 Next Steps

Now that your interface is ready:

1. **Test locally**: `npm run dev`
2. **Browse your data**: Check all tables load correctly
3. **Deploy to Vercel**: Share with collaborators
4. **Add Postgres**: When you need more power

---

## 🤝 Getting Help

**Issue with interface?**
- Check browser console (F12)
- Check terminal for errors
- Review API responses

**Need features?**
- Check `README.md` roadmap
- File an issue
- Contribute improvements

---

**Built with ❤️ using Next.js 14 • Ready for Vercel Deployment • Postgres-ready for Future**
