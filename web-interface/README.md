# Solubility Data Viewer - Web Interface

A Next.js web application for examining and browsing extracted solubility data from SDS-31 PDFs. Built for Vercel deployment with optional Postgres support for future scaling.

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open browser to http://localhost:3000
```

### Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/fetch_solubility_data)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd web-interface
vercel
```

## 📋 Features

### Current Features (CSV-based)
- ✅ Browse all extracted tables by PDF part
- ✅ Search and filter tables
- ✅ View table contents with pagination
- ✅ In-table search functionality
- ✅ Responsive design for mobile/desktop
- ✅ Fast API routes serving CSV data

### Future Features (with Postgres)
- 🔄 Full-text search across all data
- 🔄 Advanced filtering (temperature, phase, concentration ranges)
- 🔄 Data export (JSON, CSV, Excel)
- 🔄 Visualization charts
- 🔄 API for programmatic access

## 🗂️ Project Structure

```
web-interface/
├── app/
│   ├── page.tsx              # Main table browser
│   ├── table/[filename]/     # Individual table viewer
│   │   └── page.tsx
│   ├── api/
│   │   └── tables/           # API routes
│   │       ├── route.ts      # List all tables
│   │       └── [filename]/   # Get table data
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
│
├── lib/
│   └── db.ts                 # Postgres config (future)
│
├── public/                   # Static assets
├── package.json
├── next.config.js
├── tailwind.config.ts
└── vercel.json               # Vercel deployment config
```

## 🎨 UI Components

### Table Browser (`/`)
- Grid view of all tables organized by PDF part
- Search by filename
- Filter by PDF part
- Statistics dashboard
- Quick navigation

### Table Viewer (`/table/[filename]`)
- Full table display with sticky headers
- Pagination (50 rows per page)
- In-table search
- Row highlighting
- Responsive scrolling

## 🔌 API Routes

### GET `/api/tables`
Returns list of all available tables with metadata.

**Response:**
```json
{
  "success": true,
  "count": 338,
  "tables": [
    {
      "filename": "SDS-31_Part1_table_001.csv",
      "part": "Part1",
      "tableNum": 1,
      "rows": 45,
      "cols": 8,
      "size": 2048
    }
  ]
}
```

### GET `/api/tables/[filename]`
Returns full table data with parsed CSV.

**Response:**
```json
{
  "success": true,
  "metadata": {
    "filename": "SDS-31_Part1_table_001.csv",
    "part": "Part1",
    "tableNum": 1,
    "rows": 45,
    "cols": 8
  },
  "headers": ["col1", "col2", ...],
  "data": [
    {"col1": "value", "col2": "value"},
    ...
  ]
}
```

## 🗄️ Postgres Integration (Future)

### Setup Vercel Postgres

1. **Create Postgres Database**
   ```bash
   # In Vercel dashboard
   Storage → Create Database → Postgres
   ```

2. **Get Connection String**
   ```bash
   # Copy DATABASE_URL from dashboard
   # Add to .env.local
   DATABASE_URL=postgres://...
   ```

3. **Run Migration**
   ```bash
   # Import schema
   psql $DATABASE_URL < lib/schema.sql

   # Or use the migration script
   npm run migrate
   ```

4. **Import CSV Data**
   ```bash
   # Run import script (to be created)
   npm run import-csv-to-postgres
   ```

### Database Schema

The prepared schema includes:

- `solubility_data` table - Main data storage
- `table_metadata` table - Table information
- Full-text search indexes
- Optimized query indexes

See `lib/db.ts` for complete schema and query functions.

## 🎯 Data Flow

### Current (CSV-based)
```
CSV Files → API Route → Parse with Papa Parse → JSON Response → React Component
```

### Future (Postgres-based)
```
Postgres DB → Query with pg → JSON Response → React Component
```

## 🔧 Configuration

### Environment Variables

Create `.env.local`:

```bash
# Optional: Database (for future Postgres integration)
DATABASE_URL=postgres://...

# Optional: API configuration
NODE_ENV=development
```

### Vercel Configuration

The `vercel.json` configures:
- Build command: `npm run build`
- Region: `iad1` (US East)
- Output: `standalone` for optimization

## 📦 Dependencies

### Core
- **Next.js 14** - React framework with App Router
- **React 18** - UI library
- **TypeScript** - Type safety

### Data Processing
- **Papa Parse** - CSV parsing
- **pg** - Postgres client (for future)

### Styling
- **Tailwind CSS** - Utility-first CSS

## 🚀 Deployment

### Vercel (Recommended)

1. **Push to GitHub**
   ```bash
   git add web-interface/
   git commit -m "Add web interface"
   git push
   ```

2. **Import to Vercel**
   - Go to vercel.com
   - Import your repository
   - Set root directory to `web-interface`
   - Deploy!

3. **Configure Environment**
   - Add environment variables in Vercel dashboard
   - Redeploy if needed

### Manual Deployment

```bash
# Build production bundle
npm run build

# Start production server
npm start

# Or export as static site
npm run build && npm run export
```

## 🔍 Troubleshooting

### Data not loading
- Check that CSV files exist in `../output/02_cleaned/`
- Verify file permissions
- Check browser console for errors

### Build errors
- Ensure Node.js >= 18.17.0
- Clear `.next` folder: `rm -rf .next`
- Reinstall: `rm -rf node_modules && npm install`

### Vercel deployment issues
- Check build logs in Vercel dashboard
- Verify root directory is set to `web-interface`
- Check environment variables

## 📈 Performance

### Current Performance
- Initial load: ~500ms
- Table list: ~100ms
- Single table: ~200ms (small) - ~800ms (large)

### Optimization Tips
- Use pagination (already implemented)
- Enable caching for API routes
- Migrate to Postgres for large datasets (>1000 tables)
- Use CDN for static assets

## 🛣️ Roadmap

### Phase 1: MVP (Current)
- [x] Basic table browser
- [x] Table viewer with pagination
- [x] Search functionality
- [x] Vercel deployment

### Phase 2: Enhancement
- [ ] Advanced filters (temperature, phase, concentration)
- [ ] Data export (CSV, JSON, Excel)
- [ ] Responsive improvements
- [ ] Dark mode

### Phase 3: Database Migration
- [ ] Migrate to Postgres
- [ ] Full-text search
- [ ] Query API
- [ ] Performance optimization

### Phase 4: Analysis Features
- [ ] Data visualization (charts, graphs)
- [ ] Statistical analysis
- [ ] Compare tables
- [ ] Download reports

## 📝 License

Part of the fetch_solubility_data project. For examination and testing purposes.

## 🤝 Contributing

This is a development/examination interface. For improvements:

1. Test locally
2. Submit issues or PRs
3. Follow existing code structure

---

**Built with Next.js 14 • Deployed on Vercel • Ready for Postgres**
