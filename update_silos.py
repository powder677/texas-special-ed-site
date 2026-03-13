import os
import re
from bs4 import BeautifulSoup

# 1. Parse the mashed-up district string into a clean list
raw_districts = "HOUSTON ISDDALLAS ISDCYPRESS-FAIRBANKS ISDNORTHSIDE ISDKATY ISDFORT BEND ISDCONROE ISDAUSTIN ISDFORT WORTH ISDFRISCO ISDNORTH EAST ISDALDINE ISDARLINGTON ISDKLEIN ISDGARLAND ISDHUMBLE ISDEL PASO ISDLEWISVILLE ISDROUND ROCK ISDLAMAR CISDSOCORRO ISDPLANO ISDPASADENA ISDSAN ANTONIO ISDKILLEEN ISDLEANDER ISDUNITED ISDCLEAR CREEK ISDALIEF ISDMESQUITE ISDRICHARDSON ISDBROWNSVILLE ISDMANSFIELD ISDYSLETA ISDECTOR COUNTY ISDSPRING ISDEDINBURG CISDDENTON ISDCORPUS CHRISTI ISDSPRING BRANCH ISDNORTHWEST ISDKELLER ISDPROSPER ISDIRVING ISDALVIN ISDCOMAL ISDMIDLAND ISDPHARR-SAN JUAN-ALAMO ISDAMARILLO ISDGRAND PRAIRIE ISDPFLUGERVILLE ISDWYLIE ISDHALLSVILLE ISDHAYS CISDCARROLLTON-FARMERS BRANCH ISDLUBBOCK ISDGOOSE CREEK CISDEAGLE MT-SAGINAW ISDJUDSON ISDMCKINNEY ISDHURST-EULESS-BEDFORD ISDLA JOYA ISDTOMBALL ISDBIRDVILLE ISDPEARLAND ISDGALENA PARK ISDALLEN ISDMCALLEN ISDNEW CANEY ISDROCKWALL ISDLAREDO ISDTYLER ISDFORNEY ISDCROWLEY ISDHARLINGEN CISDBEAUMONT ISDBRYAN ISDWESLACO ISDSCHERTZ-CIBOLO-U CITY ISDMAGNOLIA ISDSOUTHWEST ISDABILENE ISDCOLLEGE STATION ISDGEORGETOWN ISDEAGLE PASS ISDBELTON ISDGRAPEVINE-COLLEYVILLE ISDFORT STOCKTON ISDWACO ISDBASTROP ISDCOPPELL ISDSAN ANGELO ISDDONNA ISDMISSION CISDVICTORIA ISDBURLESON ISDWICHITA FALLS ISDDICKINSON ISDCLEVELAND ISDROSCOE COLLEGIATE ISDDEER PARK ISDFRENSHIP ISDDEL VALLE ISDCANYON ISDDUNCANVILLE ISDEAST CENTRAL ISDMIDLOTHIAN ISDWAXAHACHIE ISDBRAZOSPORT ISDBOERNE ISDLAKE TRAVIS ISDHUNTSVILLE ISDSHELDON ISDHARLANDALE ISDHUTTO ISDLOS FRESNOS CISDCLINT ISDROYSE CITY ISDMANOR ISDPRINCETON ISDWALLER ISDNEW BRAUNFELS ISDMONTGOMERY ISDSHARYLAND ISDLIBERTY HILL ISDSAN FELIPE-DEL RIO CISDMEDINA VALLEY ISDCHANNELVIEW ISDWILLIS ISDSAN BENITO CISDMIDWAY ISDTEMPLE ISDRIO GRANDE CITY GRULLA ISDDRIPPING SPRINGS ISDALEDO ISDEDGEWOOD ISDSAN MARCOS CISDLONGVIEW ISDCARROLL ISDPORT ARTHUR ISDLITTLE ELM ISDLUBBOCK-COOPER ISDWEATHERFORD ISDGRANBURY ISDBARBERS HILL ISDSHERMAN ISDCOPPERAS COVE ISDMELISSA ISDTEXAS CITY ISDEANES ISDAZLE ISDSEGUIN ISDTEXARKANA ISDANGLETON ISDLA PORTE ISDHIGHLAND PARK ISDCROSBY ISDSOUTH SAN ANTONIO ISDCRANDALL ISDCLEBURNE ISDLUFKIN ISDWHITE SETTLEMENT ISDLANCASTER ISDLOCKHART ISDRED OAK ISDENNIS ISDCEDAR HILL ISDFRIENDSWOOD ISDARGYLE ISDANNA ISDJOSHUA ISDROMA ISDCORSICANA ISDGALVESTON ISDELGIN ISDNACOGDOCHES ISDCANUTILLO ISDSOUTHSIDE ISDSPLENDORA ISDDAYTON ISDFLOUR BLUFF ISDDESOTO ISDPORT NECHES-GROVES ISDCELINA ISDNEDERLAND ISDCOMMUNITY ISDGREENVILLE ISDMOUNT PLEASANT ISDGREGORY-PORTLAND ISDEVERMAN ISDDENISON ISDTERRELL ISDBRENHAM ISDALAMO HEIGHTS ISDJACKSONVILLE ISDMARSHALL ISDWHITEHOUSE ISDSOUTH TEXAS ISDLINDALE ISDKERRVILLE ISDAUBREY ISDPINE TREE ISDDUMAS ISDKAUFMAN ISDSANTA FE ISDALICE ISDSOMERSET ISDVALLEY VIEW ISDSULPHUR SPRINGS ISDANDREWS ISDSPRINGTOWN ISDVIDOR ISDJARRELL ISDLUMBERTON ISDEDCOUCH-ELSA ISDPLAINVIEW ISDFLORESVILLE ISDUVALDE CISDLIVINGSTON ISDMARBLE FALLS ISDMERCEDES ISDHEREFORD ISDMABANK ISDLOVEJOY ISDCASTLEBERRY ISDPARIS ISDALVARADO ISDDECATUR ISDCHAPEL HILL ISDCALALLEN ISDLAKE DALLAS ISDNEEDVILLE ISDHUFFMAN ISDLAMPASAS ISDSTEPHENVILLE ISDTULOSO-MIDWAY ISDLA VERNIA ISDKILGORE ISDCALHOUN COUNTY ISDBAY CITY ISDPLEASANTON ISDBROWNWOOD ISDBIG SPRING ISDGREENWOOD ISDLITTLE CYPRESS-MAURICEVILLE CISDMINERAL WELLS ISDZAPATA COUNTY ISDEL CAMPO ISDLAKE WORTH ISDHENDERSON ISDBURNET CISDGODLEY ISDBRIDGE CITY ISDPAMPA ISDNAVASOTA ISDGAINESVILLE ISDSEALY ISDSEMINOLE ISDCADDO MILLS ISDBEEVILLE ISDBURKBURNETT ISDFERRIS ISDPALESTINE ISDGILMER ISDCHINA SPRING ISDQUINLAN ISDTAYLOR ISDPECOS-BARSTOW-TOYAH ISDLA VEGA ISDSANGER ISDFREDERICKSBURG ISDCOLUMBIA-BRAZORIA ISDATHENS ISDBULLARD ISDHUDSON ISDHIDALGO ISDROCKPORT-FULTON ISDHARDIN-JEFFERSON ISDSAN ELIZARIO ISDKENNEDALE ISDROYAL ISDWILLS POINT ISDNAVARRO ISDGATESVILLE ISDLA FERIA ISDCARTHAGE ISDVAN ALSTYNE ISDWEST ORANGE-COVE CISDSILSBEE ISDLEVELLAND ISDGONZALES ISDKRUM ISDKINGSVILLE ISDWIMBERLEY ISDBROWNSBORO ISDLIBERTY ISDROBSTOWN ISDFARMERSVILLE ISDNORTH LAMAR ISDROBINSON ISD"

# Split by finding everything up to and including 'ISD' or 'CISD'
district_list = re.findall(r'.+?(?:ISD|CISD)', raw_districts)

# 2. Configure Directory Variables
# Assumes this script is run in the root folder, and there is a 'districts' folder next to it.
BASE_DIR = "districts"

def update_hub_page(file_path, slug):
    """Updates the silo-grid on the index.html page."""
    if not os.path.exists(file_path):
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml')

    grid = soup.find('div', class_='silo-grid')
    if not grid:
        return

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

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))

def update_sub_page(file_path, slug, title):
    """Updates the silo-nav on all sub-article pages."""
    if not os.path.exists(file_path):
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml')

    nav = soup.find('div', class_='silo-nav')
    if not nav:
        return

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
    nav.replace_with(new_nav)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))

# 3. Execution Loop
print(f"Starting silo update for {len(district_list)} districts...")

for d in district_list:
    # Format "HOUSTON ISD" into slug "houston-isd" and title "Houston ISD"
    slug = d.strip().lower().replace(' ', '-')
    title = d.strip().title().replace('Isd', 'ISD').replace('Cisd', 'CISD')
    
    district_folder = os.path.join(BASE_DIR, slug)
    
    # Check if the folder actually exists before processing
    if os.path.isdir(district_folder):
        # 1. Update Hub Page
        index_path = os.path.join(district_folder, 'index.html')
        update_hub_page(index_path, slug)
        
        # 2. Update Sub Pages (Assuming standard naming convention you provided)
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
            
        print(f"✅ Updated {title}")
    else:
        print(f"⚠️ Directory not found for {title} ({district_folder}) - Skipping.")

print("Finished processing all districts!")