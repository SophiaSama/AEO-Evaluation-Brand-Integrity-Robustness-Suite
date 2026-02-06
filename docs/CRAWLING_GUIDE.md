# Configuring Brand Crawl URLs

The BIRS crawler supports multiple ways to configure which URLs to crawl for brand data. This guide explains all available options.

## Quick Reference

```bash
# 1. Use specific URLs (command-line)
python scripts/crawl_brand.py --brand MyBrand --urls "https://example.com" "https://example.com/about"

# 2. Use configuration file
python scripts/crawl_brand.py --brand MyBrand --seed-urls-file data/seed_urls.json

# 3. Use built-in seeds + search (default for Manus)
python scripts/crawl_brand.py --brand Manus

# 4. Use only seed URLs, no search
python scripts/crawl_brand.py --brand Manus --no-search
```

## Configuration Methods (Priority Order)

### 1. Command-Line URLs (Highest Priority) ⭐

Use `--urls` to provide specific URLs directly:

```bash
python scripts/crawl_brand.py --brand Tesla \
  --urls \
    "https://www.tesla.com/" \
    "https://www.tesla.com/about" \
    "https://www.tesla.com/safety" \
  --max-docs 3
```

**When to use:**
- Quick one-off crawls
- Testing specific pages
- Override all other URL sources

### 2. Configuration File (Recommended for Multiple Brands) 🎯

Create a JSON file mapping brands to their seed URLs:

**File: `data/seed_urls.json`**
```json
{
  "MyBrand": [
    "https://mybrand.com/",
    "https://mybrand.com/about",
    "https://mybrand.com/products"
  ],
  "AnotherBrand": [
    "https://anotherbrand.io/",
    "https://anotherbrand.io/docs"
  ]
}
```

**Usage:**
```bash
python scripts/crawl_brand.py --brand MyBrand --seed-urls-file data/seed_urls.json
```

**When to use:**
- Testing multiple brands regularly
- Team sharing standard URL lists
- Version-controlled configurations

**Example file provided:** `data/seed_urls.example.json`

### 3. Built-in Seed URLs (Code-based)

Edit `src/crawler.py` to add built-in seeds:

```python
BRAND_SEED_URLS = {
    "manus": [
        "https://manus.im/",
        "https://manus.im/docs/introduction/welcome",
    ],
    "mybrand": [
        "https://mybrand.com/",
        "https://mybrand.com/docs/",
    ],
}
```

**Usage:**
```bash
python scripts/crawl_brand.py --brand mybrand
```

**When to use:**
- Default seeds for frequently tested brands
- When you want seeds committed to the repo

### 4. DuckDuckGo Search (Fallback)

If no URLs are provided (or not enough), the crawler searches DuckDuckGo:

```bash
# Will search for "NewBrand AI" and crawl results
python scripts/crawl_brand.py --brand NewBrand --max-docs 5
```

**Disable search:**
```bash
python scripts/crawl_brand.py --brand Manus --no-search
```

## Advanced Options

### Filter by Sentiment

Only keep pages with positive/neutral sentiment:

```bash
# Only keep pages with sentiment >= 0 (neutral or positive)
python scripts/crawl_brand.py --brand MyBrand --min-sentiment 0

# More permissive: allow slightly negative
python scripts/crawl_brand.py --brand MyBrand --min-sentiment -0.2
```

**Use case:** When search results include negative press/complaints that would skew your "clean" baseline.

### Limit Number of Documents

```bash
python scripts/crawl_brand.py --brand MyBrand --max-docs 3
```

### Combine Options

```bash
python scripts/crawl_brand.py \
  --brand Tesla \
  --urls "https://www.tesla.com/" "https://www.tesla.com/safety" \
  --max-docs 3 \
  --min-sentiment 0 \
  --no-warn-negative
```

## Examples by Use Case

### Testing a New Brand (Unknown URLs)
```bash
# Let search find URLs
python scripts/crawl_brand.py --brand NewStartup --max-docs 5
```

### Controlled Test (Specific Pages Only)
```bash
# Use exact URLs, no search
python scripts/crawl_brand.py \
  --brand MyBrand \
  --urls "https://mybrand.com/" "https://mybrand.com/whitepaper" \
  --no-search
```

### Production Config (Team Standard)
```bash
# Use shared config file
python scripts/crawl_brand.py --brand ProductA --seed-urls-file data/seed_urls.json
```

### Filter Negative Content
```bash
# Only positive/neutral content
python scripts/crawl_brand.py --brand MyBrand --min-sentiment 0
```

## URL Priority Flow

```
┌─────────────────────────────────┐
│ --urls provided?                │
│ Yes → Use these (DONE)          │
└────────────┬────────────────────┘
             │ No
             ▼
┌─────────────────────────────────┐
│ --seed-urls-file provided?      │
│ Yes → Load from JSON file       │
│       Brand found? → Use these  │
└────────────┬────────────────────┘
             │ Not found / No file
             ▼
┌─────────────────────────────────┐
│ Brand in BRAND_SEED_URLS?       │
│ Yes → Use built-in seeds        │
└────────────┬────────────────────┘
             │ No / Not enough
             ▼
┌─────────────────────────────────┐
│ --no-search flag?               │
│ No → Search DuckDuckGo          │
│ Yes → Use what we have          │
└─────────────────────────────────┘
```

## After Crawling

Always run ingestion to update ChromaDB:

```bash
python scripts/ingest_documents.py
```

## Tips

1. **Start with specific URLs** for controlled tests
2. **Use config files** for team consistency  
3. **Enable sentiment filtering** if dealing with controversial brands
4. **Disable search** (`--no-search`) for reproducible tests
5. **Check the output** - crawled content goes to `documents.json` under "clean" array

## Troubleshooting

**No documents saved?**
- Check if URLs are accessible
- Try without `--min-sentiment` filter
- Enable warnings: remove `--no-warn-negative`

**Wrong content crawled?**
- Use `--urls` to be explicit
- Add `--no-search` to avoid search results
- Check `documents.json` to verify content

**Too many negative results?**
- Use `--min-sentiment 0` or `-0.2`
- Provide explicit `--urls` for official pages only
- Use `--no-search` with curated seed URLs
