import os
import re
import csv
import io
from bs4 import BeautifulSoup

# 1. Your new CSV data block
csv_data = """District Name,Total Enrollment,Citation
BROWNSVILLE ISD,"36,140",""
HALLSVILLE ISD,"24,602",""
PEARLAND ISD,"20,862",""
GALENA PARK ISD,"20,862",""
SOUTHWEST ISD,"14,833",""
EAGLE PASS ISD,"13,820",""
FORT STOCKTON ISD,"13,480",""
CLEVELAND ISD,"12,513",""
ROSCOE COLLEGIATE ISD,"12,256",""
DEER PARK ISD,"12,165",""
FRENSHIP ISD,"11,770",""
CANYON ISD,"11,565",""
DUNCANVILLE ISD,"11,562",""
MIDLOTHIAN ISD,"11,356",""
WAXAHACHIE ISD,"11,196",""
BRAZOSPORT ISD,"11,169",""
BOERNE ISD,"11,101",""
HUNTSVILLE ISD,"10,960",""
SHELDON ISD,"10,946",""
HARLANDALE ISD,"10,835",""
HUTTO ISD,"10,688",""
LOS FRESNOS CISD,"10,357",""
MANOR ISD,"9,961",""
NEW BRAUNFELS ISD,"9,893",""
SHARYLAND ISD,"9,844",""
LIBERTY HILL ISD,"9,836",""
SAN FELIPE-DEL RIO CISD,"9,767",""
MEDINA VALLEY ISD,"9,638",""
WILLIS ISD,"9,313",""
DRIPPING SPRINGS ISD,"8,712",""
ALEDO ISD,"8,430",""
EDGEWOOD ISD,"8,384",""
CARROLL ISD,"8,105",""
PORT ARTHUR ISD,"8,041",""
LUBBOCK-COOPER ISD,"8,030",""
WEATHERFORD ISD,"8,023",""
GRANBURY ISD,"7,962",""
BARBERS HILL ISD,"7,875",""
AZLE ISD,"7,304",""
ANGLETON ISD,"7,105",""
LA PORTE ISD,"7,099",""
HIGHLAND PARK ISD,"7,073",""
SOUTH SAN ANTONIO ISD,"7,001",""
CRANDALL ISD,"6,922",""
CLEBURNE ISD,"6,877",""
LUFKIN ISD,"6,865",""
WHITE SETTLEMENT ISD,"6,831",""
LANCASTER ISD,"6,822",""
LOCKHART ISD,"6,753",""
RED OAK ISD,"6,696",""
ENNIS ISD,"6,646",""
CEDAR HILL ISD,"6,253",""
ARGYLE ISD,"6,166",""
ANNA ISD,"6,038",""
JOSHUA ISD,"6,026",""
ROMA ISD,"6,019",""
CORSICANA ISD,"5,998",""
GALVESTON ISD,"5,982",""
ELGIN ISD,"5,959",""
NACOGDOCHES ISD,"5,766",""
CANUTILLO ISD,"5,747",""
SOUTHSIDE ISD,"5,740",""
SPLENDORA ISD,"5,687",""
DAYTON ISD,"5,675",""
FLOUR BLUFF ISD,"5,559",""
DESOTO ISD,"5,389",""
PORT NECHES-GROVES ISD,"5,349",""
CELINA ISD,"5,324",""
NEDERLAND ISD,"5,317",""
COMMUNITY ISD,"5,271",""
GREENVILLE ISD,"5,218",""
MOUNT PLEASANT ISD,"5,153",""
GREGORY-PORTLAND ISD,"5,024",""
EVERMAN ISD,"5,018",""
DENISON ISD,"4,977",""
TERRELL ISD,"4,932",""
BRENHAM ISD,"4,872",""
ALAMO HEIGHTS ISD,"4,749",""
JACKSONVILLE ISD,"4,700",""
MARSHALL ISD,"4,681",""
WHITEHOUSE ISD,"4,676",""
SOUTH TEXAS ISD,"4,639",""
LINDALE ISD,"4,606",""
KERRVILLE ISD,"4,600",""
AUBREY ISD,"4,480",""
PINE TREE ISD,"4,439",""
DUMAS ISD,"4,381",""
KAUFMAN ISD,"4,356",""
ALICE ISD,"4,297",""
SOMERSET ISD,"4,259",""
VALLEY VIEW ISD,"4,250",""
SULPHUR SPRINGS ISD,"4,216",""
ANDREWS ISD,"4,209",""
SPRINGTOWN ISD,"4,188",""
VIDOR ISD,"4,165",""
JARRELL ISD,"4,157",""
LUMBERTON ISD,"4,108",""
EDCOUCH-ELSA ISD,"4,083",""
PLAINVIEW ISD,"4,077",""
FLORESVILLE ISD,"4,062",""
UVALDE CISD,"4,019",""
LIVINGSTON ISD,"4,016",""
MARBLE FALLS ISD,"4,001",""
MERCEDES ISD,"3,970",""
HEREFORD ISD,"3,964",""
MABANK ISD,"3,961",""
LOVEJOY ISD,"3,959",""
CASTLEBERRY ISD,"3,851",""
PARIS ISD,"3,832",""
ALVARADO ISD,"3,788",""
DECATUR ISD,"3,786",""
CHAPEL HILL ISD,"3,777",""
CALALLEN ISD,"3,745",""
LAKE DALLAS ISD,"3,717",""
NEEDVILLE ISD,"3,650",""
HUFFMAN ISD,"3,646",""
LAMPASAS ISD,"3,640",""
STEPHENVILLE ISD,"3,578",""
TULOSO-MIDWAY ISD,"3,566",""
LA VERNIA ISD,"3,563",""
KILGORE ISD,"3,537",""
CALHOUN COUNTY ISD,"3,514",""
BAY CITY ISD,"3,473",""
PLEASANTON ISD,"3,406",""
BROWNWOOD ISD,"3,393",""
BIG SPRING ISD,"3,376",""
GREENWOOD ISD,"3,373",""
LITTLE CYPRESS-MAURICEVILLE CISD,"3,320",""
MINERAL WELLS ISD,"3,303",""
ZAPATA COUNTY ISD,"3,290",""
EL CAMPO ISD,"3,279",""
LAKE WORTH ISD,"3,249",""
HENDERSON ISD,"3,245",""
BURNET CISD,"3,209",""
GODLEY ISD,"3,195",""
BRIDGE CITY ISD,"3,157",""
PAMPA ISD,"3,141",""
NAVASOTA ISD,"3,117",""
GAINESVILLE ISD,"3,111",""
SEALY ISD,"3,109",""
SEMINOLE ISD,"3,089",""
CADDO MILLS ISD,"3,073",""
BEEVILLE ISD,"3,033",""
BURKBURNETT ISD,"3,030",""
FERRIS ISD,"3,010",""
PALESTINE ISD,"2,995",""
GILMER ISD,"2,946",""
CHINA SPRING ISD,"2,943",""
QUINLAN ISD,"2,936",""
TAYLOR ISD,"2,930",""
PECOS-BARSTOW-TOYAH ISD,"2,919",""
LA VEGA ISD,"2,897",""
SANGER ISD,"2,880",""
FREDERICKSBURG ISD,"2,876",""
COLUMBIA-BRAZORIA ISD,"2,871",""
ATHENS ISD,"2,846",""
BULLARD ISD,"2,835",""
HUDSON ISD,"2,777",""
HIDALGO ISD,"2,771",""
ROCKPORT-FULTON ISD,"2,766",""
HARDIN-JEFFERSON ISD,"2,762",""
SAN ELIZARIO ISD,"2,755",""
KENNEDALE ISD,"2,754",""
ROYAL ISD,"2,728",""
WILLS POINT ISD,"2,716",""
NAVARRO ISD,"2,702",""
GATESVILLE ISD,"2,668",""
LA FERIA ISD,"2,667",""
CARTHAGE ISD,"2,637",""
VAN ALSTYNE ISD,"2,612",""
WEST ORANGE-COVE CISD,"2,592",""
SILSBEE ISD,"2,588",""
LEVELLAND ISD,"2,575",""
GONZALES ISD,"2,557",""
KRUM ISD,"2,542",""
KINGSVILLE ISD,"2,534",""
WIMBERLEY ISD,"2,508",""
BROWNSBORO ISD,"2,451",""
LIBERTY ISD,"2,438",""
ROBSTOWN ISD,"2,411",""
FARMERSVILLE ISD,"2,397",""
NORTH LAMAR ISD,"2,395",""
ROBINSON ISD,"2,378",""
"""

# Parse the CSV data
reader = csv.DictReader(io.StringIO(csv_data.strip()))
district_list = list(reader)

# 2. Configure Directory Variables
BASE_DIR = "districts"

def inject_silo_nav(soup, slug, title):
    """Finds or creates the silo-nav right below the h1 tag."""
    new_nav_html = f"""
    <div class="silo-nav" style="background-color: #e9ecef; padding: 14px 20px; border-radius: 8px; margin: 20px 0 30px; font-size: 15px; font-family: 'DM Sans', sans-serif; display: flex; flex-wrap: wrap; gap: 16px; align-items: center; border-left: 4px solid #6c757d;">
        <strong style="color: #334155;">{title} Resources:</strong>
        <a href="index.html" style="text-decoration: none; color: #2563eb; font-weight: 500;">District Hub</a> •
        <a href="ard-process-guide-{slug}.html" style="text-decoration: none; color: #2563eb; font-weight: 500;">ARD Guide</a> •
        <a href="evaluation-child-find-{slug}.html" style="text-decoration: none; color: #2563eb; font-weight: 500;">Evaluations (FIE)</a> •
        <a href="what-is-an-fie-{slug}.html" style="text-decoration: none; color: #2563eb; font-weight: 500;">What Is an FIE?</a> •
        <a href="how-to-request-evaluation.html" style="text-decoration: none; color: #2563eb; font-weight: 500;">Request an Eval</a> •
        <a href="grievance-dispute-resolution-{slug}.html" style="text-decoration: none; color: #2563eb; font-weight: 500;">Dispute Resolution</a>
    </div>
    """
    new_nav = BeautifulSoup(new_nav_html, 'html.parser').div
    
    existing_nav = soup.find('div', class_='silo-nav')
    if existing_nav:
        existing_nav.replace_with(new_nav)
    else:
        # If it doesn't exist, inject it right after the H1
        h1 = soup.find('h1')
        if h1:
            h1.insert_after(new_nav)
    return soup

def update_hub_page(file_path, slug, title, enrollment):
    """Updates the silo-grid, the silo-nav, and dynamically injects the enrollment number."""
    if not os.path.exists(file_path):
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml')

    # Update Silo Nav
    soup = inject_silo_nav(soup, slug, title)

    # Update Silo Grid
    grid = soup.find('div', class_='silo-grid')
    if grid:
        new_grid_html = f"""
        <div class="silo-grid">
            <a class="nav-card" href="/districts/{slug}/ard-process-guide-{slug}.html">
                <h4>ARD Process Guide</h4>
                <p>Mastering the meeting where your child's future is decided.</p>
            </a>
            <a class="nav-card" href="/districts/{slug}/evaluation-child-find-{slug}.html">
                <h4>Evaluations & Child Find</h4>
                <p>How the district identifies and evaluates students.</p>
            </a>
            <a class="nav-card" href="/districts/{slug}/what-is-an-fie-{slug}.html">
                <h4>What Is an FIE?</h4>
                <p>Understanding the Full Individual Evaluation process.</p>
            </a>
            <a class="nav-card" href="/districts/{slug}/how-to-request-evaluation.html">
                <h4>Request an Evaluation</h4>
                <p>Step-by-step guide to formally requesting an FIE.</p>
            </a>
            <a class="nav-card" href="/districts/{slug}/grievance-dispute-resolution-{slug}.html">
                <h4>Dispute Resolution</h4>
                <p>Rights and options when you disagree with a district decision.</p>
            </a>
        </div>
        """
        new_grid = BeautifulSoup(new_grid_html, 'html.parser').div
        grid.replace_with(new_grid)

    # Convert back to string to easily regex replace the exact enrollment number phrase
    html_content = str(soup)
    
    # Looks for phrases like "all 4,209 eligible students" and swaps in the correct CSV enrollment
    html_content = re.sub(r'all [0-9,]+ eligible students', f'all {enrollment} eligible students', html_content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def update_sub_page(file_path, slug, title):
    """Updates or injects the silo-nav on all sub-article pages."""
    if not os.path.exists(file_path):
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml')

    soup = inject_silo_nav(soup, slug, title)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))

# 3. Execution Loop
print(f"Starting silo update for {len(district_list)} districts...")

for row in district_list:
    raw_name = row['District Name'].strip()
    enrollment = row['Total Enrollment'].strip().replace('"', '')
    
    # Format "BROWNSVILLE ISD" into slug "brownsville-isd" and title "Brownsville ISD"
    slug = raw_name.lower().replace(' ', '-')
    title = raw_name.title().replace('Isd', 'ISD').replace('Cisd', 'CISD')
    
    district_folder = os.path.join(BASE_DIR, slug)
    
    if os.path.isdir(district_folder):
        # 1. Update Hub Page
        index_path = os.path.join(district_folder, 'index.html')
        update_hub_page(index_path, slug, title, enrollment)
        
        # 2. Update Sub Pages
        sub_pages = [
            f"ard-process-guide-{slug}.html",
            f"evaluation-child-find-{slug}.html",
            f"what-is-an-fie-{slug}.html",
            f"grievance-dispute-resolution-{slug}.html",
            "how-to-request-evaluation.html"
        ]
        
        for page in sub_pages:
            page_path = os.path.join(district_folder, page)
            update_sub_page(page_path, slug, title)
            
        print(f"✅ Updated {title} (Enrollment injected: {enrollment})")
    else:
        print(f"⚠️ Directory not found for {title} ({district_folder}) - Skipping.")

print("Finished processing all districts!")