# Texas Special Ed — District Page Generator

Generates district-specific `special-ed-updates` pages using **Vertex AI (Gemini)**,
with SEO + AEO (Answer Engine Optimization) baked in from the start.

---

## What It Produces Per District

For each district you run, the script outputs:

| File | Purpose |
|---|---|
| `{slug}/special-ed-updates.html` | Ready-to-deploy HTML page |
| `{slug}/special-ed-updates.content.json` | Raw AI-generated content (for review/editing) |

Each HTML page includes:
- **District-specific content** (not generic Texas boilerplate)
- **AEO Quick Answer box** (targets AI Overview snippets + voice search)
- **Speakable schema** (signals to Google/AI assistants what to read aloud)
- **FAQ schema** (structured data for featured snippets)
- **Article + BreadcrumbList schema**
- **Optimized meta title + description** (with year + district name)

---

## Setup

### 1. Google Cloud / Vertex AI

```bash
# Install the GCP CLI if you haven't
brew install google-cloud-sdk    # macOS
# or: https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### 2. Python dependencies

```bash
pip install google-cloud-aiplatform beautifulsoup4 jinja2 tqdm
```

### 3. Configure the script

Open `generate_district_pages.py` and set:
```python
PROJECT_ID = "your-gcp-project-id"   # line 43
```

---

## Usage

### Test with a single district first (recommended)

```bash
python generate_district_pages.py --mode single --district "Frisco ISD"
```

### Estimate cost before running all districts

```bash
python generate_district_pages.py --mode estimate
```

### Run all districts

```bash
python generate_district_pages.py --mode all
```

### Use Flash model (10x cheaper, slightly lower quality)

```bash
python generate_district_pages.py --mode all --model flash
```

### Load districts from a CSV file

```bash
python generate_district_pages.py --mode all --csv districts.csv
```

---

## Cost Reference

| Model | Input | Output | ~120 districts |
|---|---|---|---|
| Gemini 1.5 Pro | $3.50/1M tokens | $10.50/1M tokens | ~**$42** |
| Gemini 1.5 Flash | $0.35/1M tokens | $1.05/1M tokens | ~**$4** |

**Recommendation:** Generate with Flash first for all districts to review quality,
then re-run top-priority districts with Pro. Your $1,000 Vertex credit will
comfortably cover hundreds of runs.

---

## Adding Districts

### Option A: Edit the script directly

Add entries to the `DISTRICTS` list in `generate_district_pages.py`:

```python
District(
    slug="plano-isd",
    name="Plano ISD",
    county="Collin County",
    city="Plano",
    enrollment="49,000+",
    campuses="72+",
    region="DFW Metroplex",
    sped_contact_email="specialeducation@pisd.edu",
    unique_context=(
        "Plano ISD is one of the oldest established suburban districts in Collin County, "
        "with a mature special education infrastructure but persistent parent reports of "
        "slow evaluation timelines and resistance to autism spectrum eligibility."
    ),
    existing_pages=["ard-process-guide", "evaluation-child-find"],
),
```

### Option B: Use `districts.csv`

See `districts.csv` for the template format.

---

## AEO Strategy (Why This Matters)

**Answer Engine Optimization** targets AI search surfaces:
- Google AI Overviews
- Perplexity citations
- ChatGPT/Copilot web search
- Voice assistants

This script implements AEO through:

1. **Quick Answer boxes** — first thing on the page, 2-3 sentences, self-contained
2. **Speakable schema** — tells Google which CSS selectors to read aloud
3. **FAQ schema with exact-match questions** — mirrors how parents actually phrase queries
4. **Factual + law-cited answers** — AI assistants prefer citable, authoritative responses

---

## Workflow After Generation

1. **Review the `.content.json` file** for each district before deploying
2. **Spot-check contact emails** — verify they're current for each district
3. **Check unique_context accuracy** — the AI writes based on what you provide
4. **Deploy HTML files** to your server under `/districts/{slug}/special-ed-updates`
5. **Submit URLs to GSC** via the URL Inspection tool after deployment
6. **Track in Search Console** — filter by page to watch impressions climb

---

## File Structure

```
texasspecialed_generator/
├── generate_district_pages.py   # Main script
├── districts.csv                # District data (optional, alternative to inline)
├── README.md                    # This file
└── output/
    ├── generation.log           # Run logs
    └── district_pages/
        ├── frisco-isd/
        │   ├── special-ed-updates.html
        │   └── special-ed-updates.content.json
        ├── katy-isd/
        │   └── ...
        └── ...
```
