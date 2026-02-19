import os
import time
import json
import re

# ---------------------------------------------------------
# 🛑 CONFIGURATION
# ---------------------------------------------------------
SITE_DOMAIN = "https://texasspecialed.com"

# ---------------------------------------------------------
# 1. THE RESOURCES PAGE TEMPLATE
# ---------------------------------------------------------
def build_resources_page(district):
    """
    Generates the resources.html page for a specific district.
    Injects District Name, Contacts, and Leadership info into the 'Available Inventory' layout.
    """
    name = district['district_name']
    slug = district['slug']
    base_path = f"districts/{slug}"
    base_url = f"{SITE_DOMAIN}/districts/{slug}"
    
    # Leadership info (fallbacks if empty)
    director = district.get('director_name', 'Director of Special Education')
    phone = "(555) 123-4567" # Placeholder - ideally replaced with real scraped data if available
    
    # The HTML Content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Special Education Services & Support in {name} | Texas Special Ed</title>
    <meta name="description" content="Parent resource guide for Special Education in {name}. Find local advocates, evaluators, and therapy providers familiar with {name} ARD processes.">
    <link rel="stylesheet" href="../../styles/global.css">
    <link rel="stylesheet" href="../../style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <style>
        /* Specific Styles for the Ad/Resource Layout */
        
        .authority-header {{
            background-color: #f8f9fa;
            border-bottom: 4px solid #002855;
            padding: 2rem 1rem 1rem 1rem;
            text-align: center;
            margin-bottom: 1rem;
        }}
        .authority-header h1 {{
            font-size: 2.2rem;
            color: #002855;
            margin-bottom: 0.5rem;
        }}
        .authority-subtitle {{
            font-size: 1.2rem;
            color: #555;
            margin-bottom: 1.5rem;
            font-weight: 500;
        }}
        .social-proof {{
            font-size: 0.85rem;
            color: #666;
            margin-bottom: 1.5rem;
            font-style: italic;
        }}
        .district-quick-stats {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
            font-size: 0.95rem;
            color: #444;
            background: #fff;
            display: inline-flex;
            padding: 1rem 2rem;
            border-radius: 50px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .stat-item i {{
            color: #d9534f;
            margin-right: 8px;
        }}

        /* URGENCY HOOK */
        .urgency-hook {{
            background: #fff3cd;
            border: 1px solid #ffeeba;
            color: #856404;
            padding: 1rem;
            text-align: center;
            border-radius: 8px;
            margin: 0 auto 2rem auto;
            max-width: 800px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
        }}
        .urgency-hook a {{
            color: #002855;
            font-weight: bold;
            text-decoration: underline;
        }}

        /* WHO TO CALL TABLE */
        .contact-table-section {{
            max-width: 1000px;
            margin: 0 auto 2rem auto;
            background: #fff;
            border: 1px solid #eee;
            border-radius: 8px;
            overflow: hidden;
        }}
        .contact-table-header {{
            background: #002855;
            color: white;
            padding: 0.75rem 1.5rem;
            font-weight: bold;
        }}
        .contact-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            padding: 1rem;
            gap: 1rem;
        }}
        .contact-item {{
            padding: 0.5rem;
        }}
        .contact-role {{
            font-size: 0.8rem;
            text-transform: uppercase;
            color: #888;
            font-weight: bold;
            margin-bottom: 4px;
        }}
        .contact-name {{
            font-weight: 600;
            color: #333;
        }}
        .contact-phone {{
            font-size: 0.9rem;
            color: #007bff;
        }}

        /* DIRECTORY BADGES/FILTERS */
        .directory-filters {{
            max-width: 1000px;
            margin: 0 auto 2rem auto;
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            justify-content: center;
        }}
        .filter-badge {{
            background: #f8f9fa;
            border: 1px solid #ddd;
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            color: #555;
            cursor: default;
        }}
        .filter-badge i {{ margin-right: 5px; }}

        /* --- NEW: AVAILABLE SPOT STYLING (RIBBONS) --- */
        .ad-slot-available {{
            position: relative;
            overflow: hidden;
            border-style: dashed !important;
            border-color: #28a745 !important;
            background-color: #f8fff9 !important;
            opacity: 0.9;
            transition: all 0.3s ease;
        }}
        .ad-slot-available:hover {{
            transform: scale(1.01);
            box-shadow: 0 5px 15px rgba(40, 167, 69, 0.15);
        }}
        .ribbon-wrapper {{
            width: 85px;
            height: 88px;
            overflow: hidden;
            position: absolute;
            top: -3px;
            right: -3px;
        }}
        .ribbon {{
            font: bold 10px sans-serif;
            color: #333;
            text-align: center;
            transform: rotate(45deg);
            position: relative;
            padding: 5px 7px;
            background-color: #28a745;
            color: white;
            top: 15px;
            left: -5px;
            width: 120px;
            box-shadow: 0px 0px 3px rgba(0,0,0,0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        /* 2. Sponsored Hero Block (Tier 1) */
        .featured-partner-hero {{
            background: linear-gradient(to right, #ffffff, #f0f7ff);
            border: 1px solid #cce5ff;
            border-left: 5px solid #007bff;
            border-radius: 8px;
            padding: 2rem;
            margin: 0 auto 3rem auto;
            max-width: 1000px;
            box-shadow: 0 4px 15px rgba(0,123,255,0.1);
            position: relative;
            display: flex;
            align-items: center;
            gap: 2rem;
        }}
        .sponsored-badge {{
            position: absolute;
            top: 0;
            left: 0;
            background: #28a745;
            color: white;
            padding: 0.25rem 0.75rem;
            font-size: 0.75rem;
            text-transform: uppercase;
            border-bottom-right-radius: 8px;
            border-top-left-radius: 7px;
        }}
        .hero-logo-box {{
            flex: 0 0 150px;
            height: 150px;
            background: #fff;
            border: 2px dashed #ccc;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 10px;
            color: #ccc;
        }}
        .hero-content {{
            flex: 1;
        }}
        .hero-content h3 {{
            margin: 0 0 0.5rem 0;
            color: #002855;
            font-size: 1.5rem;
        }}
        .hero-tags {{
            margin: 0.5rem 0;
        }}
        .hero-tag {{
            background: #e2e6ea;
            color: #444;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            margin-right: 5px;
        }}
        .hero-cta {{
            background-color: #28a745;
            color: white;
            padding: 0.75rem 1.5rem;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            display: inline-block;
            margin-top: 1rem;
            transition: background 0.2s;
        }}
        .hero-cta:hover {{
            background-color: #218838;
        }}

        /* 3. District Process Guide (Organic Content) */
        .process-guide-section {{
            max-width: 1000px;
            margin: 0 auto 3rem auto;
        }}
        .process-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }}
        .process-card {{
            background: #fff;
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            transition: transform 0.2s;
        }}
        .process-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }}
        .process-icon {{
            font-size: 2rem;
            color: #002855;
            margin-bottom: 1rem;
        }}
        .process-card h4 {{
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
        }}
        .process-card a {{
            color: #007bff;
            font-size: 0.9rem;
            text-decoration: underline;
        }}

        /* 4. Local Service Categories */
        .service-category {{
            max-width: 1000px;
            margin: 0 auto 3rem auto;
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }}
        .category-header {{
            background: #f1f4f8;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #ddd;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .category-header h2 {{
            margin: 0;
            font-size: 1.4rem;
            color: #333;
        }}
        
        /* Tier 2: Category Featured */
        .category-featured {{
            padding: 1.5rem;
            background: #fffff8; /* Slight warmth to distinguish */
            border-bottom: 1px dashed #ddd;
            display: flex;
            gap: 1.5rem;
            align-items: flex-start;
        }}
        .cat-feat-logo {{
            width: 80px;
            height: 80px;
            background: #fff;
            border: 2px dashed #ddd;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
            color: #ccc;
        }}
        .cat-feat-content h4 {{
            margin: 0 0 0.3rem 0;
            color: #002855;
        }}
        .cat-feat-content p {{
            margin: 0 0 0.5rem 0;
            font-size: 0.95rem;
            color: #555;
        }}

        /* Tier 3: Standard List */
        .standard-listings {{
            padding: 1rem 1.5rem;
        }}
        .listing-item {{
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid #eee;
        }}
        .listing-item:last-child {{
            border-bottom: none;
        }}
        .listing-name a {{
            color: #333;
            font-weight: 600;
            text-decoration: none;
        }}
        .listing-name a:hover {{
            color: #007bff;
        }}
        .listing-contact {{
            font-size: 0.9rem;
            color: #777;
        }}

        /* Nonprofit / Community Section Styling */
        .community-resources {{
            background-color: #fafafa;
            border-top: 2px solid #eee;
            padding: 1rem 1.5rem;
        }}
        .community-label {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #888;
            font-weight: bold;
            margin-bottom: 0.5rem;
            display: block;
        }}
        .community-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px dotted #e0e0e0;
        }}
        .community-item:last-child {{ border-bottom: none; }}
        .community-name {{ font-weight: 500; color: #444; }}
        .community-desc {{ font-size: 0.85rem; color: #777; margin-left: 10px; font-style: italic;}}

        /* 5. Trust Section */
        .trust-section {{
            background: #002855;
            color: white;
            text-align: center;
            padding: 3rem 1rem;
            margin-top: 4rem;
        }}
        .trust-section h2 {{
            color: white;
            margin-bottom: 1rem;
        }}
        .trust-section p {{
            max-width: 700px;
            margin: 0 auto 2rem auto;
            line-height: 1.6;
        }}
        .partner-cta-btn {{
            background: transparent;
            border: 2px solid white;
            color: white;
            padding: 0.75rem 2rem;
            font-weight: bold;
            border-radius: 50px;
            text-decoration: none;
            transition: all 0.3s;
        }}
        .partner-cta-btn:hover {{
            background: white;
            color: #002855;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .featured-partner-hero {{
                flex-direction: column;
                text-align: center;
                gap: 1rem;
            }}
            .hero-cta {{
                width: 100%;
                text-align: center;
                box-sizing: border-box;
            }}
            .district-quick-stats {{
                flex-direction: column;
                gap: 0.5rem;
                border-radius: 10px;
                text-align: center;
            }}
        }}
    </style>
</head>
<body>

    <div id="navbar-placeholder"></div>

    <main>
        <!-- 1️⃣ AUTHORITY HEADER SECTION -->
        <section class="authority-header">
            <div class="container">
                <h1>Special Education Services in {name}</h1>
                <div class="authority-subtitle">A Parent Resource Guide for IEPs, Evaluations, and Local Providers</div>
                
                <div class="social-proof">
                    "Trusted by families navigating ARD disputes and evaluations in {name}."
                </div>

                <div class="district-quick-stats">
                    <div class="stat-item"><i class="fas fa-user-graduate"></i> {district['enrollment']} Students</div>
                    <div class="stat-item"><i class="fas fa-hands-helping"></i> ~{int(district['enrollment']*0.14)} Special Ed Enrolled</div>
                    <div class="stat-item"><i class="fas fa-phone"></i> {phone} (SpEd Office)</div>
                </div>
            </div>
        </section>

        <!-- URGENCY HOOK -->
        <div class="container">
            <div class="urgency-hook">
                <i class="fas fa-exclamation-circle fa-lg"></i>
                <div>
                    <strong>Struggling to get started?</strong> Don't wait. 
                    <a href="evaluation-child-find.html">Download the Step-by-Step Evaluation Request Template</a>
                </div>
            </div>
        </div>

        <!-- WHO TO CALL SECTION -->
        <div class="container">
            <div class="contact-table-section">
                <div class="contact-table-header">
                    <i class="fas fa-address-book" style="margin-right:8px;"></i> Who Do I Call in {name}?
                </div>
                <div class="contact-grid">
                    <div class="contact-item">
                        <div class="contact-role">Exec. Director Spec Ed</div>
                        <div class="contact-name">{director}</div>
                        <div class="contact-phone">{phone}</div>
                    </div>
                    <div class="contact-item">
                        <div class="contact-role">Evaluation Coordinator</div>
                        <div class="contact-name">Lead Diagnostician</div>
                        <div class="contact-phone">{phone}</div>
                    </div>
                    <div class="contact-item">
                        <div class="contact-role">Dyslexia Coordinator</div>
                        <div class="contact-name">District Dyslexia Coord</div>
                        <div class="contact-phone">{phone}</div>
                    </div>
                    <div class="contact-item">
                        <div class="contact-role">Records Request</div>
                        <div class="contact-name">Records Dept</div>
                        <div class="contact-phone">{phone}</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- DIRECTORY FILTERS/BADGES -->
        <div class="container">
            <div class="directory-filters">
                <span class="filter-badge"><i class="fas fa-university"></i> Nonprofits</span>
                <span class="filter-badge"><i class="fas fa-user-shield"></i> Advocates</span>
                <span class="filter-badge"><i class="fas fa-balance-scale"></i> Attorneys</span>
                <span class="filter-badge"><i class="fas fa-brain"></i> Evaluators</span>
                <span class="filter-badge"><i class="fas fa-hand-holding-heart"></i> Therapists</span>
            </div>
        </div>

        <div class="container">
            <!-- 2️⃣ SPONSORED FEATURED PARTNER BLOCK (TIER 1 - AVAILABLE) -->
            <div class="featured-partner-hero ad-slot-available">
                <div class="ribbon-wrapper"><div class="ribbon">Available</div></div>
                <div class="sponsored-badge">District Exclusive</div>
                <div class="hero-logo-box">
                    <div style="text-align:center;">
                        <i class="fas fa-plus-circle fa-2x"></i><br>
                        <small>YOUR LOGO</small>
                    </div>
                </div>
                <div class="hero-content">
                    <h3>Your Practice Name Here</h3>
                    <p><strong>Position your practice as the trusted authority in {name}.</strong> Capture high-intent parents seeking IEE evaluations, autism diagnosis, or advocacy support right when they need it most.</p>
                    <div class="hero-tags">
                        <span class="hero-tag">Exclusive Spot</span>
                        <span class="hero-tag">High Visibility</span>
                        <span class="hero-tag">District-Wide</span>
                    </div>
                    <a href="../../contact-us/index.html" class="hero-cta">Reserve This Exclusive Spot</a>
                </div>
            </div>

            <!-- 3️⃣ DISTRICT PROCESS GUIDE (THE "HOOK") -->
            <section class="process-guide-section">
                <h3 style="border-left: 4px solid #002855; padding-left: 10px; color: #002855; margin-bottom:1.5rem;">Navigating Special Ed in {name}</h3>
                <div class="process-grid">
                    <div class="process-card">
                        <div class="process-icon"><i class="fas fa-file-signature"></i></div>
                        <h4>Requesting Evaluation</h4>
                        <p style="font-size:0.9rem; color:#666; margin-bottom:1rem;">How to submit a written request to Child Find.</p>
                        <a href="evaluation-child-find.html">Get the Template &rarr;</a>
                    </div>
                    <div class="process-card">
                        <div class="process-icon"><i class="fas fa-users"></i></div>
                        <h4>ARD Meetings</h4>
                        <p style="font-size:0.9rem; color:#666; margin-bottom:1rem;">Understanding your role in the Admission, Review, and Dismissal process.</p>
                        <a href="ard-process-guide.html">View Process Guide &rarr;</a>
                    </div>
                    <div class="process-card">
                        <div class="process-icon"><i class="fas fa-book-open"></i></div>
                        <h4>Dyslexia Services</h4>
                        <p style="font-size:0.9rem; color:#666; margin-bottom:1rem;">Recent changes to the Texas Dyslexia Handbook.</p>
                        <a href="../../files/dyslexia-toolkit-2026.pdf">Download Toolkit &rarr;</a>
                    </div>
                    <div class="process-card">
                        <div class="process-icon"><i class="fas fa-gavel"></i></div>
                        <h4>Dispute Resolution</h4>
                        <p style="font-size:0.9rem; color:#666; margin-bottom:1rem;">What to do if you disagree with the evaluation.</p>
                        <a href="grievance-dispute-resolution.html">Learn Rights &rarr;</a>
                    </div>
                </div>
            </section>

            <!-- 4️⃣ LOCAL SERVICE CATEGORIES (TIER 2 & 3 ADS + NONPROFITS) -->
            
            <!-- Category: Advocates -->
            <div class="service-category">
                <div class="category-header">
                    <h2>Advocates & ARD Support</h2>
                    <span style="font-size:0.8rem; color:#888;">Serving {district['city']} Area</span>
                </div>
                
                <!-- Tier 2 Ad (Available) -->
                <div class="category-featured ad-slot-available">
                    <div class="ribbon-wrapper"><div class="ribbon">Available</div></div>
                    <div class="cat-feat-logo">
                        <i class="fas fa-user-plus fa-lg"></i>
                    </div>
                    <div class="cat-feat-content">
                        <h4>Your Advocacy Firm Here</h4>
                        <p>Be the first advocate parents call when they hit a wall with the district. Secure this category-exclusive placement.</p>
                        <a href="../../contact-us/index.html" style="font-size:0.9rem; font-weight:bold; color:#28a745;">Claim This Category &rarr;</a>
                    </div>
                </div>

                <!-- Nonprofit Section -->
                <div class="community-resources">
                    <span class="community-label">Community & Nonprofit Resources</span>
                    <div class="community-item">
                        <span class="community-name">Partners Resource Network (TEAM Project)</span>
                        <span class="community-desc">Free parent training & workshops.</span>
                    </div>
                </div>

                <!-- Tier 3 Ads (Available) -->
                <div class="standard-listings">
                    <div class="listing-item" style="color:#999; font-style:italic;">
                        <div class="listing-name">Standard Listing Available</div>
                        <div class="listing-contact"><a href="../../contact-us/index.html" style="color:#28a745;">List Your Service</a></div>
                    </div>
                </div>
            </div>

            <!-- Category: Attorneys -->
            <div class="service-category" style="margin-top: 3rem;">
                <div class="category-header">
                    <h2>Special Education Attorneys</h2>
                    <span style="font-size:0.8rem; color:#888;">Legal Representation & Due Process</span>
                </div>
                
                <!-- Tier 2 Ad (Available) -->
                <div class="category-featured ad-slot-available">
                    <div class="ribbon-wrapper"><div class="ribbon">Available</div></div>
                    <div class="cat-feat-logo">
                        <i class="fas fa-balance-scale fa-lg"></i>
                    </div>
                    <div class="cat-feat-content">
                        <h4>Your Law Firm Here</h4>
                        <p>Parents on this page are researching Due Process and Mediation. Position your firm as their legal defense.</p>
                        <a href="../../contact-us/index.html" style="font-size:0.9rem; font-weight:bold; color:#28a745;">Claim This Category &rarr;</a>
                    </div>
                </div>

                 <!-- Nonprofit Section -->
                 <div class="community-resources">
                    <span class="community-label">Legal Aid & Rights</span>
                    <div class="community-item">
                        <span class="community-name">Disability Rights Texas</span>
                        <span class="community-desc">Statewide protection & advocacy agency (Legal Aid).</span>
                    </div>
                </div>
            </div>

            <!-- Category: Therapy Services -->
            <div class="service-category" style="margin-top: 3rem;">
                <div class="category-header">
                    <h2>Autism Therapy & ABA</h2>
                    <span style="font-size:0.8rem; color:#888;">Clinic & In-Home</span>
                </div>
                
                <!-- Tier 2 Ad (Available) -->
                <div class="category-featured ad-slot-available">
                    <div class="ribbon-wrapper"><div class="ribbon">Available</div></div>
                    <div class="cat-feat-logo">
                        <i class="fas fa-puzzle-piece fa-lg"></i>
                    </div>
                    <div class="cat-feat-content">
                        <h4>Your Therapy Center Here</h4>
                        <p>Connect with parents seeking ABA, Speech, or OT services in {name}. Exclusive category placement.</p>
                        <a href="../../contact-us/index.html" style="font-size:0.9rem; font-weight:bold; color:#28a745;">Claim This Category &rarr;</a>
                    </div>
                </div>
            </div>
            
        </div>

        <!-- 5️⃣ TRUST SECTION -->
        <section class="trust-section">
            <div class="container">
                <h2>Why Partner With Us?</h2>
                <p>We are the only independent, data-driven resource hub for Texas special education parents. Our district pages capture high-intent traffic from families actively seeking evaluations, advocates, and legal support.</p>
                <div style="margin-top:2rem;">
                    <a href="../../contact-us/index.html" class="partner-cta-btn">Become a Partner</a>
                    <p style="margin-top:1rem; font-size:0.8rem; opacity:0.6;">*Only one Featured Partner per category per district.*</p>
                </div>
            </div>
        </section>
    </main>

    <div id="footer-placeholder"></div>

    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            fetch('../../navbar.json')
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('navbar-placeholder').innerHTML = data.html;
                }});
            
            fetch('../../footer.json')
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('footer-placeholder').innerHTML = data.html;
                }});
        }});
    </script>
</body>
</html>"""

    # WRITE THE FILE
    with open(f"{base_path}/resources.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"  [+] Built resources.html for {name}")

# ---------------------------------------------------------
# CSV PARSING LOGIC (Keep from original script)
# ---------------------------------------------------------
def clean_row(line):
    line = line.strip()
    if line.startswith('"') and line.endswith('"'): line = line[1:-1]
    parts = [p.strip() for p in line.split(',')]
    if len(parts) < 2: return None
    try:
        name = parts[0].strip()
        if not name or name.isdigit(): return None
        enrollment_str = parts[1].replace('"', '').replace('.', '').strip()
        enrollment = int(enrollment_str) if enrollment_str.isdigit() else 0
        district_type = "Urban" if enrollment > 20000 else "Rural"
        city_raw = parts[2].strip() if len(parts) >= 3 else ""
        slug = re.sub(r'[^a-z0-9\-]', '', re.sub(r'\s+', '-', name.lower())).strip('-')
        email_base = re.sub(r'[^a-z0-9]', '', name.lower().replace(' isd', '').replace(' cisd', ''))
        director_email = f"sped@{email_base}.edu"
        return {
            "district_name": name, "slug": slug, "city": city_raw, "enrollment": enrollment,
            "director_name": "Director of Special Education", "director_email": director_email, "type": district_type
        }
    except Exception: return None

# ---------------------------------------------------------
# MAIN RUNNER
# ---------------------------------------------------------
if __name__ == "__main__":
    print("📂 Reading district data...")
    # NOTE: Ensure 'texas_districts_data.csv' exists in the same directory
    if not os.path.exists('texas_districts_data.csv'):
        print("❌ Error: 'texas_districts_data.csv' not found. Please upload it.")
        exit()

    with open('texas_districts_data.csv', 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    districts = []
    for line in lines[1:]:
        if not line.strip(): continue
        d = clean_row(line)
        if d: districts.append(d)

    print(f"✅ Found {len(districts)} districts. Generating Resource Hubs...")

    for district in districts:
        slug = district['slug']
        # Ensure directory exists
        os.makedirs(f"districts/{slug}", exist_ok=True)
        
        # Build the new page
        build_resources_page(district)

    print("\n✅ All Resource Hub pages generated successfully!")