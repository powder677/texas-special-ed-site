import os
import re

# Configuration
BASE_DISTRICTS_DIR = "./districts"

# Data provided by user - Normalized to handle duplicates/typos
DISTRICT_DATA = """
BROWNSVILLE ISD,"36,140"

"""

# Common shared CSS and Header/Footer components
COMMON_HEAD = """
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;600;700&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet"/>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f8fafc; }
        h1 { font-size: clamp(1.8rem, 5vw, 2.5rem); font-family: 'Lora', serif; color: #0a2342; text-align: center; margin-bottom: 1.5rem; line-height: 1.2; }
        .layout-grid { max-width: 900px; margin: 0 auto; width: 100%; }
        .content-column { font-family: 'Source Sans 3', sans-serif; font-size: 17px; line-height: 1.8; color: #1e293b; background: #fff; padding: 40px 60px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0; margin-bottom: 40px; }
        h2 { font-family: 'Lora', serif; font-size: 1.8rem; font-weight: 700; color: #0a2342; margin: 2.5rem 0 1rem; padding-top: 1.5rem; border-top: 2px solid #f1f5f9; }
        h3 { font-family: 'Lora', serif; font-size: 1.4rem; font-weight: 700; color: #1e3a8a; margin: 1.5rem 0 0.75rem; }
        .silo-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 2rem 0; }
        .nav-card { background: #fff; border: 1px solid #e2e8f0; padding: 15px; border-radius: 10px; text-decoration: none !important; transition: all 0.2s ease; display: flex; flex-direction: column; }
        .nav-card:hover { border-color: #1a56db; transform: translateY(-2px); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .nav-card h4 { font-family: 'Lora', serif; font-size: 1.1rem; color: #1a56db; margin: 0 0 5px; font-weight: 700; }
        .nav-card p { font-size: 13px; color: #64748b; margin: 0; }
        .ai-tool-banner { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: white; border-radius: 16px; padding: 40px; margin: 3rem 0; text-align: center; }
        .btn-gold { background: #d4af37; color: #0f172a !important; padding: 14px 28px; border-radius: 8px; font-weight: 800; text-decoration: none; display: inline-block; cursor: pointer; border: none; }
        @media (max-width: 768px) { .content-column { padding: 30px 20px !important; margin: 0 !important; border-radius: 0 !important; border: none !important; } }
        #ai-modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.8); z-index: 10000; backdrop-filter: blur(4px); }
        .modal-content { background: white; max-width: 600px; width: 95%; margin: 20px auto; border-radius: 16px; overflow: hidden; font-family: sans-serif; }
    </style>
"""

# Page Templates
PAGE_CONFIG = {
    "index.html": {
        "title": "Special Education | Parent Resource Hub",
        "description": "Complete guide for parents in {{DISTRICT_MIXED}}.",
        "content": """
        <h1>{{DISTRICT_UPPER}} Special Education: Parent Resource Hub</h1>
        <p class="text-lg text-slate-600 mb-8">If your child has a disability or you suspect they need support, this guide explains exactly how to access services, understand your rights, and advocate effectively within {{DISTRICT_MIXED}}.</p>
        
        {{SILO_NAV}}

        <div class="ai-tool-banner">
            <span class="bg-[#d4af37] text-slate-900 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest mb-3 inline-block">Live AI Tool</span>
            <h3 class="text-white mt-0 border-none pt-0">Free ARD Rights Scan</h3>
            <p class="text-blue-100 text-lg mt-2 mb-6">Wondering if {{DISTRICT_MIXED}} violated your child's rights? Get an instant analysis based on Texas law.</p>
            <button onclick="openRightsScan()" class="btn-gold">Run My Free ARD Scan →</button>
        </div>

        <h2>Understanding {{DISTRICT_MIXED}} Special Education</h2>
        <p>Special education in {{DISTRICT_UPPER}} is individualized instruction designed to meet the unique needs of students with disabilities. Under federal law (IDEA), the district must provide a Free Appropriate Public Education (FAPE) to its {{ENROLLMENT}} eligible students.</p>
        
        <h3>How to Request an Evaluation</h3>
        <p>As a parent in {{DISTRICT_MIXED}}, you have the right to request a comprehensive evaluation at any time. The district has 15 school days to respond to your request.</p>
        """
    },
    "ard-process-guide.html": {
        "title": "ARD Meeting Guide",
        "description": "Master the ARD process in {{DISTRICT_MIXED}}.",
        "content": """
        <h1>The ARD Process Guide for {{DISTRICT_MIXED}} Parents</h1>
        <p class="text-lg text-slate-600 mb-8">The Admission, Review, and Dismissal (ARD) meeting is where your child's IEP is created. You are a critical member of this team.</p>
        
        {{SILO_NAV}}

        <h2>Your Rights at the Table</h2>
        <p>You have the right to participate in all decisions. If {{DISTRICT_MIXED}} proposes a change, they must provide Prior Written Notice at least 5 school days in advance.</p>
        
        <div class="ai-tool-banner">
            <h3 class="text-white mt-0 border-none pt-0">Need an ARD Meeting Script?</h3>
            <p class="text-blue-100 text-lg mt-2 mb-6">Our AI tool drafts specific scripts and goals for your next meeting.</p>
            <a href="/resources/Iep-letter" class="btn-gold">Get ARD Support — $25 →</a>
        </div>
        """
    },
    "evaluation-child-find.html": {
        "title": "Evaluation & Child Find",
        "description": "Requesting a Full Individual Evaluation in {{DISTRICT_MIXED}}.",
        "content": """
        <h1>Evaluations & Child Find in {{DISTRICT_MIXED}}</h1>
        <p class="text-lg text-slate-600 mb-8">Child Find is a legal requirement for {{DISTRICT_MIXED}} to identify and evaluate students suspected of having a disability.</p>
        
        {{SILO_NAV}}

        <h2>The Evaluation Timeline</h2>
        <p>Once you provide consent, the district has 45 school days to complete the Full Individual Evaluation (FIE) and another 30 calendar days to hold the ARD meeting.</p>
        """
    },
    "grievance-dispute-resolution.html": {
        "title": "Dispute Resolution & Grievances",
        "description": "How to handle disagreements with {{DISTRICT_MIXED}}.",
        "content": """
        <h1>Dispute & Discipline Rights in {{DISTRICT_MIXED}}</h1>
        <p class="text-lg text-slate-600 mb-8">Disagreements with {{DISTRICT_MIXED}} are common. Knowing the formal resolution pathways is essential.</p>
        
        {{SILO_NAV}}

        <div class="ai-tool-banner">
            <span class="bg-[#d4af37] text-slate-900 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest mb-3 inline-block">Live AI Tool</span>
            <h3 class="text-white mt-0 border-none pt-0">Free ARD Rights Scan</h3>
            <p class="text-blue-100 text-lg mt-2 mb-6">If the school violated your child's rights, our AI tool helps you identify the exact regulation to cite.</p>
            <button onclick="openRightsScan()" class="btn-gold">Run Analysis →</button>
        </div>
        """
    },
    "dyslexia-services.html": {
        "title": "Dyslexia & 504 Services",
        "description": "Accessing reading supports in {{DISTRICT_MIXED}}.",
        "content": """
        <h1>Dyslexia & 504 Services in {{DISTRICT_MIXED}}</h1>
        <p class="text-lg text-slate-600 mb-8">Students with dyslexia in {{DISTRICT_MIXED}} often receive support under Section 504 or IDEA.</p>
        
        {{SILO_NAV}}

        <h2>The Dyslexia Handbook</h2>
        <p>Texas requirements for dyslexia instruction are strict. {{DISTRICT_MIXED}} must provide evidence-based, multisensory instruction for identified students.</p>
        """
    }
}

def clean_slug(name):
    slug = name.lower().strip()
    slug = slug.replace("isd", "isd").replace("cisd", "cisd") # normalize
    slug = re.sub(r'[^a-z0-9 ]', '', slug) # remove punctuation
    slug = slug.replace(" ", "-")
    slug = re.sub(r'-+', '-', slug) # fix multiple dashes
    # Consolidation logic: Standardize variations to 'brownsville-isd'
    if slug in ["brownsvill", "brownsville"]: 
        slug = "brownsville-isd"
    return slug

def to_mixed_case(name):
    words = name.split()
    return " ".join([w.capitalize() if w.upper() not in ["ISD", "CISD"] else w.upper() for w in words])

def generate_silo_nav(slug):
    return f"""
        <div class="silo-grid">
            <a href="/districts/{slug}/index.html" class="nav-card"><h4>Home</h4><p>District Overview</p></a>
            <a href="/districts/{slug}/ard-process-guide.html" class="nav-card"><h4>ARD Guide</h4><p>Meeting Support</p></a>
            <a href="/districts/{slug}/evaluation-child-find.html" class="nav-card"><h4>Evaluations</h4><p>Request Testing</p></a>
            <a href="/districts/{slug}/grievance-dispute-resolution.html" class="nav-card"><h4>Disputes</h4><p>Grievance Rights</p></a>
            <a href="/districts/{slug}/dyslexia-services.html" class="nav-card"><h4>Dyslexia</h4><p>Reading Services</p></a>
        </div>
    """

def deploy():
    if not os.path.exists(BASE_DISTRICTS_DIR): os.makedirs(BASE_DISTRICTS_DIR)
    
    processed_slugs = set()
    lines = [line.strip() for line in DISTRICT_DATA.strip().split("\n") if line.strip()]
    
    for line in lines:
        match = re.search(r'^(.*?),"(.*?)"', line)
        if not match: continue
        
        raw_name, enrollment = match.group(1).strip(), match.group(2).strip()
        slug = clean_slug(raw_name)
        
        # Consolidation check: ensures Brownsville and Brownsville ISD use the same folder
        if slug in processed_slugs: 
            print(f"Consolidating alias into existing silo: {raw_name} -> {slug}")
            continue
        processed_slugs.add(slug)
        
        mixed_name = to_mixed_case(raw_name)
        district_path = os.path.join(BASE_DISTRICTS_DIR, slug)
        if not os.path.exists(district_path): os.makedirs(district_path)
            
        for filename, config in PAGE_CONFIG.items():
            # Build Full Page
            full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    {COMMON_HEAD}
    <title>{mixed_name} {config['title']}</title>
    <meta name="description" content="{config['description'].replace('{{DISTRICT_MIXED}}', mixed_name)}"/>
</head>
<body>
    <header class="bg-white border-b border-slate-200 py-4 mb-8">
        <div class="max-w-7xl mx-auto px-4 flex justify-between items-center">
            <a href="/" class="text-xl font-bold text-[#0a2342] font-serif">Texas <span class="text-blue-600 italic font-normal">Special Ed</span></a>
            <nav class="hidden md:flex space-x-6 text-sm font-semibold text-slate-600">
                <a href="/" class="hover:text-blue-600">Home</a>
                <a href="/districts/index.html" class="hover:text-blue-600">Districts</a>
                <a href="/resources/index.html" class="hover:text-blue-600">Resources</a>
            </nav>
        </div>
    </header>
    <div class="layout-grid">
        <article class="content-column">
            {config['content']}
        </article>
    </div>
    
    <!-- AI MODAL SYSTEM -->
    <div id="ai-modal-overlay">
        <div class="modal-content">
            <div class="p-6 bg-slate-900 text-white flex justify-between items-center">
                <h3 class="text-xl font-serif m-0">ARD Rights Analysis</h3>
                <button onclick="closeRightsScan()" class="text-white cursor-pointer">&times;</button>
            </div>
            <div class="p-8" id="modal-body">
                <textarea id="situation-text" rows="5" class="w-full border border-slate-300 rounded-lg p-3 text-base" placeholder="Describe the situation in {mixed_name}..."></textarea>
                <button onclick="runAnalysis()" id="run-scan-btn" class="w-full bg-blue-600 text-white py-4 rounded-xl font-bold mt-4">Start Analysis</button>
                <div id="analysis-content" class="mt-4 text-slate-700"></div>
            </div>
        </div>
    </div>
    <script>
        const apiKey = "";
        function openRightsScan() {{ document.getElementById('ai-modal-overlay').style.display='block'; }}
        function closeRightsScan() {{ document.getElementById('ai-modal-overlay').style.display='none'; }}
        async function runAnalysis() {{
            const sit = document.getElementById('situation-text').value;
            const btn = document.getElementById('run-scan-btn');
            if(!sit) return; btn.innerText = "Analyzing...";
            try {{
                const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${{apiKey}}`, {{
                    method:'POST', headers:{{'Content-Type':'application/json'}},
                    body: JSON.stringify({{ contents: [{{ parts: [{{ text: "Texas Special Ed analysis for {mixed_name}: " + sit }}] }}] }})
                }});
                const d = await r.json();
                document.getElementById('analysis-content').innerHTML = d.candidates[0].content.parts[0].text.replace(/\\n/g, '<br>');
            }} catch(e) {{ }} finally {{ btn.innerText = "Start Analysis"; }}
        }}
    </script>
</body>
</html>"""
            # Substitutions
            full_html = full_html.replace("{{DISTRICT_UPPER}}", raw_name)
            full_html = full_html.replace("{{DISTRICT_MIXED}}", mixed_name)
            full_html = full_html.replace("{{ENROLLMENT}}", enrollment)
            full_html = full_html.replace("{{SILO_NAV}}", generate_silo_nav(slug))
            
            with open(os.path.join(district_path, filename), "w", encoding="utf-8") as f:
                f.write(full_html)
                
    print(f"Deployment complete. Generated silos for {len(processed_slugs)} unique districts.")

if __name__ == "__main__":
    deploy()