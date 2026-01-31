# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a modular RSS feed generator for manga and other content sources. Each RSS source is implemented as a standalone Python script in `sources/`, and `generate_all.py` orchestrates running all sources to generate RSS XML files in `output/`.

The project is designed for zero-dependency deployment via GitHub Actions, which automatically updates RSS feeds on a schedule.

## Architecture

### Core Components

**generate_all.py** - Main orchestrator
- Discovers all RSS source files in `sources/` (excludes files starting with `_`)
- Runs each source script as a subprocess with 30-second timeout
- Collects and reports results
- Each source runs independently; one failure doesn't block others

**sources/*.py** - Individual RSS generators
- Each file is a self-contained RSS generator that can run independently
- Must define these constants: `RSS_FILENAME`, `RSS_TITLE`, `RSS_DESCRIPTION`, source URL constant
- Must implement `main()` function that returns 0 on success, non-zero on failure
- Should output to `output/` directory (relative to project root)
- Pattern: fetch content → parse items → generate RSS XML → write to output/

**output/** - Generated RSS files
- RSS XML files committed to git for GitHub Pages/raw.githubusercontent.com access
- File names should match source file names (e.g., `yirenzhixia.py` → `yirenzhixia.xml`)

### RSS Generation Pattern

All sources follow this structure:
1. Fetch remote content (HTML/API) with proper User-Agent headers and timeout
2. Parse content using BeautifulSoup or similar
3. Generate RSS 2.0 XML with xml.etree.ElementTree
4. Include atom:link self-reference and proper RFC822 dates
5. Pretty-print XML with xml.dom.minidom for readability

## Common Commands

### Local Development

```bash
# Generate all RSS feeds
python3 generate_all.py

# Generate single RSS source
python3 sources/yirenzhixia.py

# Test a specific source and view output
python3 sources/SOURCE_NAME.py && cat output/SOURCE_NAME.xml
```

### Installing Dependencies

```bash
pip install requests beautifulsoup4
```

Dependencies are minimal by design:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing

### GitHub Actions

The workflow `.github/workflows/update-rss.yml` runs hourly via cron. To manually trigger:
- Go to Actions tab → "Update All RSS Feeds" → "Run workflow"

Workflow permissions must be set to "Read and write permissions" in Settings → Actions → General.

## Adding New RSS Sources

1. Create `sources/new_source.py` based on existing source template (e.g., `yirenzhixia.py`)
2. Define required constants: source URL, `RSS_FILENAME`, `RSS_TITLE`, `RSS_DESCRIPTION`
3. Implement fetch, parse, and RSS generation logic
4. Test locally: `python3 sources/new_source.py`
5. Verify output: check `output/new_source.xml` is valid RSS
6. Commit both source file and generated XML

No changes to `generate_all.py` needed - it auto-discovers new sources.

## Code Conventions

**File Naming**
- Source files: lowercase with underscores (e.g., `manga_name.py`)
- Output files: match source names (e.g., `manga_name.xml`)

**Error Handling**
- Print errors to stderr using `file=sys.stderr`
- Return non-zero exit code on failure
- Use try-except for network requests with timeouts (10 seconds recommended)

**Output Format**
- Status messages to stdout: "正在生成...", "✓ RSS文件已生成"
- Progress indicators help understand long-running operations
- `generate_all.py` displays source name, status emoji (✓/✗), and summary

**Path Handling**
- Use `Path(__file__).parent` to get script directory
- Output directory is always `project_root / 'output'`
- Create output directory with `exist_ok=True`

## Project Language

Documentation and code comments are primarily in Chinese (Simplified). Console output and user-facing messages should also be in Chinese.

## Testing RSS Validity

After generating RSS files, validate with:
- RSS validators: https://validator.w3.org/feed/
- Test in RSS reader (NetNewsWire, Feedly, etc.)
- Check XML is well-formed: `xmllint --noout output/*.xml`

## GitHub Deployment

RSS files are accessed via:
```
https://raw.githubusercontent.com/USERNAME/localRSS/main/output/SOURCE_NAME.xml
```

Changes to `sources/` trigger automatic regeneration via push event in GitHub Actions.
