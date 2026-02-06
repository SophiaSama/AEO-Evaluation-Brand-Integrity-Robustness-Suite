# URL Configuration Enhancement - Summary

## What Was Added

Enhanced the BIRS crawler to support flexible URL configuration for different brands and testing scenarios.

## New Features

### 1. **Configuration File Support** 🆕
- New `--seed-urls-file` option to load brand URLs from JSON
- Example file: `data/seed_urls.example.json`
- Format: `{"BrandName": ["url1", "url2", ...]}`

### 2. **Enhanced BRAND_SEED_URLS Dictionary** 🔄
- Replaced single `MANUS_SEED_URLS` with `BRAND_SEED_URLS` dict
- Supports multiple brands in code
- Backward compatible (MANUS_SEED_URLS still exists)

### 3. **Improved Command-line Interface** ✨
- Better help text with examples
- Clearer priority explanation
- Added usage examples in `--help`

### 4. **Comprehensive Documentation** 📚
- New guide: `docs/CRAWLING_GUIDE.md`
- Updated README with configuration examples
- Clear priority order explanation

## How to Configure URLs

### Option 1: Command-line (Quick)
```bash
python scripts/crawl_brand.py --brand Tesla --urls "https://tesla.com/" "https://tesla.com/about"
```

### Option 2: Configuration File (Recommended)
Create `data/seed_urls.json`:
```json
{
  "Tesla": ["https://tesla.com/", "https://tesla.com/about"],
  "OpenAI": ["https://openai.com/"]
}
```

Run:
```bash
python scripts/crawl_brand.py --brand Tesla --seed-urls-file data/seed_urls.json
```

### Option 3: Built-in Seeds (Code)
Edit `src/crawler.py`:
```python
BRAND_SEED_URLS = {
    "manus": [...],
    "tesla": ["https://tesla.com/"],
}
```

## URL Priority Order

1. `--urls` (command-line) - **Highest priority**
2. `--seed-urls-file` (config file)
3. `BRAND_SEED_URLS` (built-in)
4. DuckDuckGo search (fallback)

## Files Modified

- ✅ `scripts/crawl_brand.py` - Added config file support and better help
- ✅ `src/crawler.py` - Enhanced BRAND_SEED_URLS dictionary
- ✅ `data/seed_urls.example.json` - Example configuration
- ✅ `docs/CRAWLING_GUIDE.md` - Comprehensive guide
- ✅ `README.md` - Updated with URL configuration info

## Use Cases

### Controlled Testing
```bash
# Exact URLs, no search
python scripts/crawl_brand.py --brand MyBrand \
  --urls "https://mybrand.com/" --no-search
```

### Team Standard
```bash
# Use shared config
python scripts/crawl_brand.py --brand ProductA \
  --seed-urls-file data/seed_urls.json
```

### Filter Negative Content
```bash
# Only positive/neutral pages
python scripts/crawl_brand.py --brand MyBrand \
  --urls "https://mybrand.com/" --min-sentiment 0
```

## Benefits

✅ **Flexibility** - Multiple configuration methods  
✅ **Team Collaboration** - Shared config files  
✅ **Version Control** - Config files tracked in git  
✅ **Reproducibility** - Same URLs every time  
✅ **Easy Testing** - Quick command-line overrides  

## Example Workflow

1. **Create your brand config:**
   ```bash
   cp data/seed_urls.example.json data/seed_urls.json
   # Edit to add your brand
   ```

2. **Crawl with config:**
   ```bash
   python scripts/crawl_brand.py --brand YourBrand --seed-urls-file data/seed_urls.json
   ```

3. **Ingest to ChromaDB:**
   ```bash
   python scripts/ingest_documents.py
   ```

4. **Run tests:**
   ```bash
   python -m src.run_suite
   ```
