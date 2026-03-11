#!/usr/bin/env python3
"""
Batch API ISD Page Generator - MAXIMUM COST EFFICIENCY
Uses Anthropic's Batch API for 50% discount on already cheap Haiku pricing
Processes all 185 districts for ~$4.50 instead of ~$9 with regular API
"""

import anthropic
import json
import time
import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-haiku-4-5-20251001"  # Haiku 4.5 - cheapest and best for batch
BATCH_DIR = "/home/claude/batch_requests"
OUTPUT_DIR = "/home/claude/generated_pages"

# ISD Data - same as before
ISD_DATA = """District Name,Total Enrollment,Citation
BROWNSVILLE ISD,36140,[cite: 1]
HALLSVILLE ISD,24602,[cite: 1]
PEARLAND ISD,20862,[cite: 1]
GALENA PARK ISD,20862,[cite: 1]
SOUTHWEST ISD,14833,[cite: 2]
EAGLE PASS ISD,13820,[cite: 2]
FORT STOCKTON ISD,13480,[cite: 2]
CLEVELAND ISD,12513,[cite: 2]
ROSCOE COLLEGIATE ISD,12256,[cite: 2]
DEER PARK ISD,12165,[cite: 2]
FRENSHIP ISD,11770,[cite: 2]
CANYON ISD,11565,[cite: 2]
DUNCANVILLE ISD,11562,[cite: 2]
MIDLOTHIAN ISD,11356,[cite: 2]
WAXAHACHIE ISD,11196,[cite: 2]
BRAZOSPORT ISD,11169,[cite: 2]
BOERNE ISD,11101,[cite: 2]
HUNTSVILLE ISD,10960,[cite: 2]
SHELDON ISD,10946,[cite: 2]
HARLANDALE ISD,10835,[cite: 2]
HUTTO ISD,10688,[cite: 2]
LOS FRESNOS CISD,10357,[cite: 2]
MANOR ISD,9961,[cite: 2]
NEW BRAUNFELS ISD,9893,[cite: 2]
SHARYLAND ISD,9844,[cite: 2]
LIBERTY HILL ISD,9836,[cite: 2]
SAN FELIPE-DEL RIO CISD,9767,[cite: 2]
MEDINA VALLEY ISD,9638,[cite: 2]
WILLIS ISD,9313,[cite: 2]
DRIPPING SPRINGS ISD,8712,[cite: 2]
ALEDO ISD,8430,[cite: 2]
EDGEWOOD ISD,8384,[cite: 2]
CARROLL ISD,8105,[cite: 2]
PORT ARTHUR ISD,8041,[cite: 2]
LUBBOCK-COOPER ISD,8030,[cite: 2]
WEATHERFORD ISD,8023,[cite: 2]
GRANBURY ISD,7962,[cite: 2]
BARBERS HILL ISD,7875,[cite: 2]
AZLE ISD,7304,[cite: 3]
ANGLETON ISD,7105,[cite: 3]
LA PORTE ISD,7099,[cite: 3]
HIGHLAND PARK ISD,7073,[cite: 3]
SOUTH SAN ANTONIO ISD,7001,[cite: 3]
CRANDALL ISD,6922,[cite: 3]
CLEBURNE ISD,6877,[cite: 3]
LUFKIN ISD,6865,[cite: 3]
WHITE SETTLEMENT ISD,6831,[cite: 3]
LANCASTER ISD,6822,[cite: 3]
LOCKHART ISD,6753,[cite: 3]
RED OAK ISD,6696,[cite: 3]
ENNIS ISD,6646,[cite: 3]
CEDAR HILL ISD,6253,[cite: 3]
ARGYLE ISD,6166,[cite: 3]
ANNA ISD,6038,[cite: 3]
JOSHUA ISD,6026,[cite: 3]
ROMA ISD,6019,[cite: 3]
CORSICANA ISD,5998,[cite: 3]
GALVESTON ISD,5982,[cite: 3]
ELGIN ISD,5959,[cite: 3]
NACOGDOCHES ISD,5766,[cite: 3]
CANUTILLO ISD,5747,[cite: 3]
SOUTHSIDE ISD,5740,[cite: 3]
SPLENDORA ISD,5687,[cite: 3]
DAYTON ISD,5675,[cite: 3]
FLOUR BLUFF ISD,5559,[cite: 3]
DESOTO ISD,5389,[cite: 3]
PORT NECHES-GROVES ISD,5349,[cite: 3]
CELINA ISD,5324,[cite: 3]
NEDERLAND ISD,5317,[cite: 3]
COMMUNITY ISD,5271,[cite: 3]
GREENVILLE ISD,5218,[cite: 3]
MOUNT PLEASANT ISD,5153,[cite: 3]
GREGORY-PORTLAND ISD,5024,[cite: 3]
EVERMAN ISD,5018,[cite: 3]
DENISON ISD,4977,[cite: 3]
TERRELL ISD,4932,[cite: 3]
BRENHAM ISD,4872,[cite: 3]
ALAMO HEIGHTS ISD,4749,[cite: 3]
JACKSONVILLE ISD,4700,[cite: 3]
MARSHALL ISD,4681,[cite: 3]
WHITEHOUSE ISD,4676,[cite: 3]
SOUTH TEXAS ISD,4639,[cite: 3]
LINDALE ISD,4606,[cite: 3]
KERRVILLE ISD,4600,[cite: 3]
AUBREY ISD,4480,[cite: 3]
PINE TREE ISD,4439,[cite: 3]
DUMAS ISD,4381,[cite: 3]
KAUFMAN ISD,4356,[cite: 3]
ALICE ISD,4297,[cite: 3]
SOMERSET ISD,4259,[cite: 3]
VALLEY VIEW ISD,4250,[cite: 3]
SULPHUR SPRINGS ISD,4216,[cite: 3]
ANDREWS ISD,4209,[cite: 3]
SPRINGTOWN ISD,4188,[cite: 3]
VIDOR ISD,4165,[cite: 3]
JARRELL ISD,4157,[cite: 3]
LUMBERTON ISD,4108,[cite: 3]
EDCOUCH-ELSA ISD,4083,[cite: 3]
PLAINVIEW ISD,4077,[cite: 3]
FLORESVILLE ISD,4062,[cite: 3]
UVALDE CISD,4019,[cite: 3]
LIVINGSTON ISD,4016,[cite: 3]
MARBLE FALLS ISD,4001,[cite: 3]
MERCEDES ISD,3970,[cite: 3]
HEREFORD ISD,3964,[cite: 3]
MABANK ISD,3961,[cite: 3]
LOVEJOY ISD,3959,[cite: 3]
CASTLEBERRY ISD,3851,[cite: 3]
PARIS ISD,3832,[cite: 3]
ALVARADO ISD,3788,[cite: 3]
DECATUR ISD,3786,[cite: 3]
CHAPEL HILL ISD,3777,[cite: 3]
CALALLEN ISD,3745,[cite: 3]
LAKE DALLAS ISD,3717,[cite: 3]
NEEDVILLE ISD,3650,[cite: 4]
HUFFMAN ISD,3646,[cite: 4]
LAMPASAS ISD,3640,[cite: 4]
STEPHENVILLE ISD,3578,[cite: 4]
TULOSO-MIDWAY ISD,3566,[cite: 4]
LA VERNIA ISD,3563,[cite: 4]
KILGORE ISD,3537,[cite: 4]
CALHOUN COUNTY ISD,3514,[cite: 4]
BAY CITY ISD,3473,[cite: 4]
PLEASANTON ISD,3406,[cite: 4]
BROWNWOOD ISD,3393,[cite: 4]
BIG SPRING ISD,3376,[cite: 4]
GREENWOOD ISD,3373,[cite: 4]
LITTLE CYPRESS-MAURICEVILLE CISD,3320,[cite: 4]
MINERAL WELLS ISD,3303,[cite: 4]
ZAPATA COUNTY ISD,3290,[cite: 4]
EL CAMPO ISD,3279,[cite: 4]
LAKE WORTH ISD,3249,[cite: 4]
HENDERSON ISD,3245,[cite: 4]
BURNET CISD,3209,[cite: 4]
GODLEY ISD,3195,[cite: 4]
BRIDGE CITY ISD,3157,[cite: 4]
PAMPA ISD,3141,[cite: 4]
NAVASOTA ISD,3117,[cite: 4]
GAINESVILLE ISD,3111,[cite: 4]
SEALY ISD,3109,[cite: 4]
SEMINOLE ISD,3089,[cite: 4]
CADDO MILLS ISD,3073,[cite: 4]
BEEVILLE ISD,3033,[cite: 4]
BURKBURNETT ISD,3030,[cite: 4]
FERRIS ISD,3010,[cite: 4]
PALESTINE ISD,2995,[cite: 4]
GILMER ISD,2946,[cite: 4]
CHINA SPRING ISD,2943,[cite: 4]
QUINLAN ISD,2936,[cite: 4]
TAYLOR ISD,2930,[cite: 4]
PECOS-BARSTOW-TOYAH ISD,2919,[cite: 4]
LA VEGA ISD,2897,[cite: 4]
SANGER ISD,2880,[cite: 4]
FREDERICKSBURG ISD,2876,[cite: 4]
COLUMBIA-BRAZORIA ISD,2871,[cite: 4]
ATHENS ISD,2846,[cite: 4]
BULLARD ISD,2835,[cite: 4]
HUDSON ISD,2777,[cite: 4]
HIDALGO ISD,2771,[cite: 4]
ROCKPORT-FULTON ISD,2766,[cite: 4]
HARDIN-JEFFERSON ISD,2762,[cite: 4]
SAN ELIZARIO ISD,2755,[cite: 4]
KENNEDALE ISD,2754,[cite: 4]
ROYAL ISD,2728,[cite: 4]
WILLS POINT ISD,2716,[cite: 4]
NAVARRO ISD,2702,[cite: 4]
GATESVILLE ISD,2668,[cite: 4]
LA FERIA ISD,2667,[cite: 4]
CARTHAGE ISD,2637,[cite: 4]
VAN ALSTYNE ISD,2612,[cite: 4]
WEST ORANGE-COVE CISD,2592,[cite: 4]
SILSBEE ISD,2588,[cite: 4]
LEVELLAND ISD,2575,[cite: 4]
GONZALES ISD,2557,[cite: 4]
KRUM ISD,2542,[cite: 4]
KINGSVILLE ISD,2534,[cite: 4]
WIMBERLEY ISD,2508,[cite: 4]
BROWNSBORO ISD,2451,[cite: 4]
LIBERTY ISD,2438,[cite: 4]
ROBSTOWN ISD,2411,[cite: 4]
FARMERSVILLE ISD,2397,[cite: 4]
NORTH LAMAR ISD,2395,[cite: 4]
ROBINSON ISD,2378,[cite: 4]"""

PAGE_CONFIGS = [
    {
        "filename": "index.html",
        "title_template": "{district} Special Education Resources | Parent Rights Guide",
        "meta_template": "Complete special education resource hub for {district} families. ARD rights, FIE timelines, dyslexia services, and discipline defense - all in one place.",
        "purpose": "Main district hub page with overview of all special education resources",
        "keywords": ["special education", "ARD meeting", "IEP services", "parent rights", "dyslexia program"]
    },
    {
        "filename": "evaluation-child-find.html",
        "title_template": "How to Request an Evaluation in {district} | FIE Timeline",
        "meta_template": "Learn the 45 school-day FIE timeline, Child Find obligations, and how to submit a written evaluation request to {district}.",
        "purpose": "Complete guide to requesting a Full Individual Evaluation (FIE) in this specific district",
        "keywords": ["FIE evaluation", "child find", "special education evaluation", "45 day timeline", "evaluation request"]
    },
    {
        "filename": "ard-process-guide.html",
        "title_template": "{district} ARD Meeting Guide | IEP Process & Parent Rights",
        "meta_template": "Navigate ARD meetings in {district} with confidence. Learn your rights, meeting procedures, IEP development, and how to prepare.",
        "purpose": "Step-by-step guide to ARD (Admission, Review, and Dismissal) meetings and IEP process",
        "keywords": ["ARD meeting", "IEP process", "ARD rights", "ARD preparation", "IEP goals"]
    },
    {
        "filename": "grievance-dispute-resolution.html",
        "title_template": "{district} Special Education Complaints | Dispute Resolution",
        "meta_template": "File grievances, request mediation, or pursue due process for special education disputes in {district}. Know your legal options.",
        "purpose": "Guide to filing complaints and resolving disputes with the district",
        "keywords": ["special education complaint", "due process", "mediation", "TEA complaint", "dispute resolution"]
    },
    {
        "filename": "como-solicitar-una-evaluacion-fie.html",
        "title_template": "Cómo Solicitar una Evaluación FIE en {district} | Guía en Español",
        "meta_template": "Guía completa en español para solicitar una evaluación de educación especial en {district}. Cronología de 45 días, derechos de los padres.",
        "purpose": "Spanish-language guide to requesting special education evaluation",
        "keywords": ["evaluación especial", "educación especial", "FIE español", "derechos padres", "solicitar evaluación"]
    }
]


def parse_isd_data() -> List[Dict]:
    """Parse the ISD data into a list of dictionaries"""
    isds = []
    for line in ISD_DATA.strip().split('\n')[1:]:
        parts = line.split(',')
        if len(parts) >= 2:
            name = parts[0].strip()
            enrollment_str = parts[1].strip().strip('"').replace(',', '')
            try:
                enrollment = int(enrollment_str)
            except:
                enrollment = 0
            
            slug = name.lower().replace(' isd', '').replace(' cisd', '').replace(' ', '-')
            
            isds.append({
                'name': name,
                'enrollment': enrollment,
                'slug': slug
            })
    
    return isds


def create_seo_prompt(district: Dict, page_config: Dict) -> str:
    """Create SEO-optimized prompt"""
    
    district_name = district['name']
    enrollment = district['enrollment']
    district_city = district_name.replace(' ISD', '').replace(' CISD', '')
    
    keywords = [
        f"{district_name} {kw}" for kw in page_config['keywords']
    ]
    keywords.extend([
        f"{district_city} special education",
        f"special education attorney near {district_city}",
        f"special ed advocate {district_city}"
    ])
    
    return f"""You are an expert SEO content writer specializing in local search optimization for Texas school districts and special education services.

TASK: Write a comprehensive {page_config['purpose']}.

DISTRICT CONTEXT:
- District: {district_name}
- Enrollment: {enrollment:,} students
- Location: {district_city}, Texas
- Audience: Parents of special needs children in {district_name}

SEO REQUIREMENTS (CRITICAL FOR LOCAL SEARCH DOMINANCE):

1. PRIMARY LONG-TAIL KEYWORDS (use naturally 2-3 times each):
   {chr(10).join(f'   - "{kw}"' for kw in keywords[:8])}

2. DISTRICT NAME OPTIMIZATION:
   - Mention "{district_name}" 10-15 times naturally throughout
   - Use variations: "in {district_name}", "for {district_name} parents", "{district_name} families"
   - Reference "{district_city}" area 3-5 times

3. CONTENT STRUCTURE:
   - Start with H1: Clear, keyword-rich title mentioning {district_name}
   - Use 5-8 H2 sections covering key topics
   - Include H3 subsections for detailed points
   - Write 1000-1400 words total

4. PARENT-FOCUSED VALUE:
   - Answer specific questions parents ask
   - Include actionable steps and timelines
   - Reference Texas Education Code sections where relevant
   - Use empathetic, supportive tone
   - Add specific examples and scenarios

5. LOCAL SIGNALS:
   - Mention nearby cities if relevant to {district_city}
   - Reference Texas-specific procedures
   - Include phrases like "parents in {district_name}" or "{district_name} families"

6. READABILITY:
   - Short paragraphs (3-4 sentences)
   - Bulleted and numbered lists
   - Bold key terms and important deadlines
   - Use clear, jargon-free language

RESPONSE FORMAT:
- Return ONLY the article body as clean HTML
- Start with <h1> tag
- Use semantic HTML: <h2>, <h3>, <p>, <ul>, <ol>, <strong>, <em>
- NO DOCTYPE, head, navigation, footer, forms, or JavaScript
- NO opening pleasantries or meta-commentary

TONE: Empowering, authoritative, accessible, supportive"""


def create_batch_request_file(isds: List[Dict]):
    """Create the JSONL batch request file"""
    
    batch_dir = Path(BATCH_DIR)
    batch_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_file = batch_dir / f"isd_pages_batch_{timestamp}.jsonl"
    
    requests = []
    
    for district in isds:
        for page_config in PAGE_CONFIGS:
            custom_id = f"{district['slug']}_{page_config['filename'].replace('.html', '')}"
            
            prompt = create_seo_prompt(district, page_config)
            
            request = {
                "custom_id": custom_id,
                "params": {
                    "model": MODEL,
                    "max_tokens": 4096,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            }
            
            requests.append(request)
    
    # Write to JSONL file
    with open(batch_file, 'w') as f:
        for request in requests:
            f.write(json.dumps(request) + '\n')
    
    print(f"✓ Created batch file: {batch_file}")
    print(f"  Total requests: {len(requests)}")
    print(f"  File size: {batch_file.stat().st_size / 1024:.1f} KB")
    
    return batch_file


def submit_batch_job(client: anthropic.Anthropic, batch_file: Path):
    """Submit the batch job to Anthropic API"""
    
    print(f"\nSubmitting batch job...")
    
    # Read and parse the JSONL file
    requests = []
    with open(batch_file, 'r') as f:
        for line in f:
            if line.strip():
                requests.append(json.loads(line))
    
    print(f"  Parsed {len(requests)} requests from file")
    
    # Submit the batch
    batch = client.messages.batches.create(
        requests=requests
    )
    
    print(f"✓ Batch job submitted!")
    print(f"  Batch ID: {batch.id}")
    print(f"  Status: {batch.processing_status}")
    print(f"  Request counts: {batch.request_counts}")
    
    return batch.id


def check_batch_status(client: anthropic.Anthropic, batch_id: str):
    """Check status of batch job"""
    
    batch = client.messages.batches.retrieve(batch_id)
    
    print(f"\nBatch Status: {batch.processing_status}")
    print(f"  Requests Succeeded: {batch.request_counts.get('succeeded', 0)}")
    print(f"  Requests Failed: {batch.request_counts.get('errored', 0)}")
    print(f"  Requests Processing: {batch.request_counts.get('processing', 0)}")
    
    if batch.processing_status == 'ended':
        if batch.results_url:
            print(f"  Results URL: {batch.results_url}")
            return True
    
    return False


def download_and_process_results(client: anthropic.Anthropic, batch_id: str, isds: List[Dict]):
    """Download results and create HTML files"""
    
    print(f"\nDownloading results for batch {batch_id}...")
    
    # Get batch results
    results = []
    for result in client.messages.batches.results(batch_id):
        results.append(result)
    
    print(f"✓ Downloaded {len(results)} results")
    
    # Create output directory
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each result
    for result in results:
        custom_id = result.custom_id
        slug, page_type = custom_id.rsplit('_', 1)
        
        # Find matching district and page config
        district = next((d for d in isds if d['slug'] == slug), None)
        page_config = next((p for p in PAGE_CONFIGS if page_type in p['filename']), None)
        
        if not district or not page_config:
            print(f"✗ Could not match {custom_id}")
            continue
        
        # Extract AI content
        if hasattr(result.result, 'message'):
            ai_content = result.result.message.content[0].text
            
            # Create full HTML page
            full_html = create_full_html_page(district, page_config, ai_content)
            
            # Save file
            district_dir = output_dir / district['slug']
            district_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = district_dir / page_config['filename']
            output_file.write_text(full_html, encoding='utf-8')
            
            print(f"✓ Created {district['slug']}/{page_config['filename']}")


def create_full_html_page(district: Dict, page_config: Dict, ai_content: str) -> str:
    """Wrap AI content in full HTML template"""
    
    title = page_config['title_template'].format(district=district['name'])
    meta_desc = page_config['meta_template'].format(district=district['name'])
    canonical = f"https://www.texasspecialed.com/districts/{district['slug']}/{page_config['filename'].replace('.html', '')}"
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-GVLPE273XH"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-GVLPE273XH');
</script>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{title}</title>
<meta name="description" content="{meta_desc}"/>
<link rel="canonical" href="{canonical}"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;600;700&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet"/>
<link href="/style.css" rel="stylesheet"/>
<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    margin: 0;
    padding: 0;
    background: #f8fafc;
}}
.container {{ max-width: 1100px; margin: 0 auto; padding: 20px; }}
.site-header {{ background: #fff; padding: 15px 20px; border-bottom: 1px solid #ddd; }}
h1 {{ font-family: 'Lora', serif; font-size: 2.4rem; color: #0a2342; margin: 20px 0; line-height: 1.2;}}
.content-column {{ font-family: 'Source Sans 3', sans-serif; font-size: 17px; line-height: 1.75; color: #1a1a2e; background: #fff; padding: 40px; border-radius: 8px; margin-top: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);}}
.content-column h2 {{ font-family: 'Lora', serif; font-size: 1.6rem; font-weight: 700; color: #0a2342; margin: 2.5rem 0 1rem;}}
.content-column h3 {{ font-family: 'Lora', serif; font-size: 1.3rem; font-weight: 600; color: #0a2342; margin: 2rem 0 0.8rem;}}
.content-column p {{ margin: 0 0 1.25rem; }}
.content-column ul, .content-column ol {{ margin: 1rem 0; padding-left: 2rem; }}
.content-column li {{ margin-bottom: 0.5rem; }}
.content-column strong {{ color: #0a2342; font-weight: 600; }}
</style>
</head>
<body>
<header class="site-header">
<nav class="navbar">
<a href="/" class="text-logo">Texas <em>Special Ed</em></a>
</nav>
</header>
<main class="container">
<article class="content-column">
{ai_content}
</article>
</main>
<footer style="text-align: center; padding: 40px 20px; color: #64748b;">
<p>© 2026 Texas Special Education Resources. All rights reserved.</p>
</footer>
</body>
</html>'''


def main():
    """Main execution function"""
    
    if not ANTHROPIC_API_KEY:
        print("ERROR: Please set ANTHROPIC_API_KEY environment variable")
        print('  export ANTHROPIC_API_KEY="sk-ant-..."')
        return
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    isds = parse_isd_data()
    
    total_requests = len(isds) * len(PAGE_CONFIGS)
    estimated_cost = total_requests * 0.007  # ~$0.007 per page based on actual batch pricing
    
    print(f"\n{'='*70}")
    print(f"BATCH API ISD PAGE GENERATOR - MAXIMUM COST EFFICIENCY")
    print(f"{'='*70}")
    print(f"Districts: {len(isds)}")
    print(f"Pages per district: {len(PAGE_CONFIGS)}")
    print(f"Total requests: {total_requests}")
    print(f"Estimated cost: ${estimated_cost:.2f} (50% off with Batch API!)")
    print(f"{'='*70}\n")
    
    # Step 1: Create batch request file
    print("Step 1: Creating batch request file...")
    batch_file = create_batch_request_file(isds)
    
    # Step 2: Submit batch job
    print("\nStep 2: Submitting batch job...")
    response = input("Submit batch job? (y/N): ")
    if response.lower() != 'y':
        print("Aborted. You can submit later using the batch file:")
        print(f"  {batch_file}")
        return
    
    batch_id = submit_batch_job(client, batch_file)
    
    # Step 3: Monitor status
    print(f"\nStep 3: Monitoring batch job...")
    print("Batch jobs typically complete in 1-24 hours depending on volume.")
    print(f"Check status anytime with batch ID: {batch_id}")
    print("\nTo check status and download results, run:")
    print(f"  python3 batch_isd_pages_api.py --check {batch_id}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 2 and sys.argv[1] == '--check':
        # Check and download results mode
        batch_id = sys.argv[2]
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        isds = parse_isd_data()
        
        if check_batch_status(client, batch_id):
            download_and_process_results(client, batch_id, isds)
    else:
        # Normal batch creation mode
        main()