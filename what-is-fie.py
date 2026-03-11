import os

# Your complete list of districts
DISTRICT_DATA = """
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

EN_OUTPUT_DIR = "districts"

# The HTML Template for the 'What is an FIE' page
FIE_TEMPLATE = """<h1>What is an FIE (Full Individual Evaluation) in {district_name}?</h1>

<p>If you are exploring special education services for your child, you will frequently hear the term FIE. An FIE, or <strong>Full Individual Evaluation</strong>, is a comprehensive process that examines your child's development, health, vision, hearing, and academic performance. It serves as the critical first step toward getting appropriate support if you suspect your child has a learning disability or developmental delay.</p>

<h2>What Does the Evaluation Cover?</h2>
<p>In {district_name}, an FIE comprehensively evaluates all relevant aspects of your child's development. The assessment typically includes cognitive testing, achievement testing, behavioral observation, and input from both teachers and parents. Specific areas evaluated include:</p>
<ul>
    <li>Academic skills (reading, writing, math)</li>
    <li>Language and communication skills</li>
    <li>Motor functioning (gross and fine)</li>
    <li>Hearing and vision</li>
    <li>Social and emotional functioning</li>
    <li>Cognitive ability and general development</li>
</ul>

<h2>Who Conducts the FIE in {district_name}?</h2>
<p>All evaluations must be conducted by qualified professionals at no cost to your family. Depending on your child's specific needs, the evaluation team may include:</p>
<ul>
    <li><strong>School psychologists:</strong> To conduct cognitive and behavioral assessments</li>
    <li><strong>Special education teachers:</strong> To assess academic achievement</li>
    <li><strong>Speech-language pathologists:</strong> If speech or language concerns exist</li>
    <li><strong>Occupational or physical therapists:</strong> If fine or gross motor concerns exist</li>
    <li><strong>School counselors or social workers:</strong> For behavioral or emotional concerns</li>
</ul>

<h2>What is the Purpose of the FIE?</h2>
<p>The primary goal of the FIE is to determine if your child qualifies for special education services under federal and Texas state laws, such as the Individuals with Disabilities Education Act (IDEA). Once testing is complete, {district_name} compiles a comprehensive report explaining what was tested, how your child performed, and whether they meet the eligibility criteria.</p>

<h2>How Much Does it Cost?</h2>
<p>In {district_name}, special education evaluations are <strong>completely free for all students</strong>. The district is actively looking for students who might benefit from these services through their child find system, and the cost can never be passed on to parents.</p>"""

def generate_fie_pages():
    count = 0
    # Process the text block line by line
    for line in DISTRICT_DATA.strip().split('\n'):
        if not line:
            continue
            
        # Parse the district name before the first comma (e.g., "BROWNSVILLE ISD")
        full_district_name = line.split(',')[0].strip('"').strip()
        
        # Determine folder name format (matches your previous script's folder names)
        # e.g., "BROWNSVILLE ISD" -> "brownsville"
        # e.g., "LOS FRESNOS CISD" -> "los-fresnos"
        folder_slug = full_district_name.replace(" ISD", "").replace(" CISD", "").strip().lower().replace(" ", "-")
        
        # Create directory if it doesn't exist
        district_dir = os.path.join(EN_OUTPUT_DIR, folder_slug)
        os.makedirs(district_dir, exist_ok=True)
        
        # Inject the full district name into the template
        page_html = FIE_TEMPLATE.format(district_name=full_district_name)
        
        # Create and write the what-is-fie.html file
        file_path = os.path.join(district_dir, "what-is-fie.html")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(page_html)
            
        count += 1

    print(f"✅ Success! Generated {count} 'what-is-fie.html' pages inside the '{EN_OUTPUT_DIR}' directory.")

if __name__ == "__main__":
    generate_fie_pages()