import os
import re
from bs4 import BeautifulSoup
from pathlib import Path

# --- CONFIGURATION ---
# Update this path to your local project directory
BASE_DIR = Path(r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts")
TEMPLATE_FILE = Path("template.html")

# The list provided by the user
DISTRICT_LIST_RAW = """
HOUSTON ISD DALLAS ISD CYPRESS-FAIRBANKS ISD NORTHSIDE ISD KATY ISD FORT BEND ISD CONROE ISD AUSTIN ISD FORT WORTH ISD FRISCO ISD NORTH EAST ISD ALDINE ISD ARLINGTON ISD KLEIN ISD GARLAND ISD HUMBLE ISD EL PASO ISD LEWISVILLE ISD ROUND ROCK ISD LAMAR CISD SOCORRO ISD PLANO ISD PASADENA ISD SAN ANTONIO ISD KILLEEN ISD LEANDER ISD UNITED ISD CLEAR CREEK ISD ALIEF ISD MESQUITE ISD RICHARDSON ISD BROWNSVILLE ISD MANSFIELD ISD YSLETA ISD ECTOR COUNTY ISD SPRING ISD EDINBURG CISD DENTON ISD CORPUS CHRISTI ISD SPRING BRANCH ISD NORTHWEST ISD KELLER ISD PROSPER ISD IRVING ISD ALVIN ISD COMAL ISD MIDLAND ISD PHARR-SAN JUAN-ALAMO ISD AMARILLO ISD GRAND PRAIRIE ISD PFLUGERVILLE ISD WYLIE ISD HALLSVILLE ISD HAYS CISD CARROLLTON-FARMERS BRANCH ISD LUBBOCK ISD GOOSE CREEK CISD EAGLE MT-SAGINAW ISD JUDSON ISD MCKINNEY ISD HURST-EULESS-BEDFORD ISD LA JOYA ISD TOMBALL ISD BIRDVILLE ISD PEARLAND ISD GALENA PARK ISD ALLEN ISD MCALLEN ISD NEW CANEY ISD ROCKWALL ISD LAREDO ISD TYLER ISD FORNEY ISD CROWLEY ISD HARLINGEN CISD BEAUMONT ISD BRYAN ISD WESLACO ISD SCHERTZ-CIBOLO-U CITY ISD MAGNOLIA ISD SOUTHWEST ISD ABILENE ISD COLLEGE STATION ISD GEORGETOWN ISD EAGLE PASS ISD BELTON ISD GRAPEVINE-COLLEYVILLE ISD FORT STOCKTON ISD WACO ISD BASTROP ISD COPPELL ISD SAN ANGELO ISD DONNA ISD MISSION CISD VICTORIA ISD BURLESON ISD WICHITA FALLS ISD DICKINSON ISD CLEVELAND ISD ROSCOE COLLEGIATE ISD DEER PARK ISD FRENSHIP ISD DEL VALLE ISD CANYON ISD DUNCANVILLE ISD EAST CENTRAL ISD MIDLOTHIAN ISD WAXAHACHIE ISD BRAZOSPORT ISD BOERNE ISD LAKE TRAVIS ISD HUNTSVILLE ISD SHELDON ISD HARLANDALE ISD HUTTO ISD LOS FRESNOS CISD CLINT ISD ROYSE CITY ISD MANOR ISD PRINCETON ISD WALLER ISD NEW BRAUNFELS ISD MONTGOMERY ISD SHARYLAND ISD LIBERTY HILL ISD SAN FELIPE-DEL RIO CISD MEDINA VALLEY ISD CHANNELVIEW ISD WILLIS ISD SAN BENITO CISD MIDWAY ISD TEMPLE ISD RIO GRANDE CITY GRULLA ISD DRIPPING SPRINGS ISD ALEDO ISD EDGEWOOD ISD SAN MARCOS CISD LONGVIEW ISD CARROLL ISD PORT ARTHUR ISD LITTLE ELM ISD LUBBOCK-COOPER ISD WEATHERFORD ISD GRANBURY ISD BARBERS HILL ISD SHERMAN ISD COPPERAS COVE ISD MELISSA ISD TEXAS CITY ISD EANES ISD AZLE ISD SEGUIN ISD TEXARKANA ISD ANGLETON ISD LA PORTE ISD HIGHLAND PARK ISD CROSBY ISD SOUTH SAN ANTONIO ISD CRANDALL ISD CLEBURNE ISD LUFKIN ISD WHITE SETTLEMENT ISD LANCASTER ISD LOCKHART ISD RED OAK ISD ENNIS ISD CEDAR HILL ISD FRIENDSWOOD ISD ARGYLE ISD ANNA ISD JOSHUA ISD ROMA ISD CORSICANA ISD GALVESTON ISD ELGIN ISD NACOGDOCHES ISD CANUTILLO ISD SOUTHSIDE ISD SPLENDORA ISD DAYTON ISD FLOUR BLUFF ISD DESOTO ISD PORT NECHES-GROVES ISD CELINA ISD NEDERLAND ISD COMMUNITY ISD GREENVILLE ISD MOUNT PLEASANT ISD GREGORY-PORTLAND ISD EVERMAN ISD DENISON ISD TERRELL ISD BRENHAM ISD ALAMO HEIGHTS ISD JACKSONVILLE ISD MARSHALL ISD WHITEHOUSE ISD SOUTH TEXAS ISD LINDALE ISD KERRVILLE ISD AUBREY ISD PINE TREE ISD DUMAS ISD KAUFMAN ISD SANTA FE ISD ALICE ISD SOMERSET ISD VALLEY VIEW ISD SULPHUR SPRINGS ISD ANDREWS ISD SPRINGTOWN ISD VIDOR ISD JARRELL ISD LUMBERTON ISD EDCOUCH-ELSA ISD PLAINVIEW ISD FLORESVILLE ISD UVALDE CISD LIVINGSTON ISD MARBLE FALLS ISD MERCEDES ISD HEREFORD ISD MABANK ISD LOVEJOY ISD CASTLEBERRY ISD PARIS ISD ALVARADO ISD DECATUR ISD CHAPEL HILL ISD CALALLEN ISD LAKE DALLAS ISD NEEDVILLE ISD HUFFMAN ISD LAMPASAS ISD STEPHENVILLE ISD TULOSO-MIDWAY ISD LA VERNIA ISDKILGORE ISD CALHOUN COUNTY ISD BAY CITY ISD PLEASANTON ISD BROWNWOOD ISD BIG SPRING ISD GREENWOOD ISD LITTLE CYPRESS-MAURICEVILLE CISD MINERAL WELLS ISD ZAPATA COUNTY ISD EL CAMPO ISD LAKE WORTH ISD HENDERSON ISD BURNET CISD GODLEY ISD BRIDGE CITY ISD PAMPA ISD NAVASOTA ISD GAINESVILLE ISD SEALY ISD SEMINOLE ISD CADDO MILLS ISD BEEVILLE ISD BURKBURNETT ISD FERRIS ISD PALESTINE ISD GILMER ISD CHINA SPRING ISD QUINLAN ISD TAYLOR ISD PECOS-BARSTOW-TOYAH ISD LA VEGA ISD SANGER ISD FREDERICKSBURG ISD COLUMBIA-BRAZORIA ISD ATHENS ISD BULLARD ISD HUDSON ISD HIDALGO ISD ROCKPORT-FULTON ISD HARDIN-JEFFERSON ISD SAN ELIZARIO ISD KENNEDALE ISD ROYAL ISD WILLS POINT ISD NAVARRO ISD GATESVILLE ISD LA FERIA ISD CARTHAGE ISD VAN ALSTYNE ISD WEST ORANGE-COVE CISD SILSBEE ISD LEVELLAND ISD GONZALES ISD KRUM ISD KINGSVILLE ISD WIMBERLEY ISD BROWNSBORO ISD LIBERTY ISD ROBSTOWN ISD FARMERSVILLE ISD NORTH LAMAR ISD ROBINSON ISD
"""

def get_slug(name):
    """Converts 'AUSTIN ISD' to 'austin-isd'."""
    return name.strip().lower().replace(" ", "-").replace("/", "-")

def parse_districts(raw_text):
    """Simple parser to find all occurrences of 'ISD' or 'CISD' patterns."""
    pattern = r".+? (?:ISD|CISD)"
    matches = re.findall(pattern, raw_text)
    return [m.strip() for m in matches]

def main():
    districts = parse_districts(DISTRICT_LIST_RAW)
    
    if not TEMPLATE_FILE.exists():
        print("Error: template.html not found.")
        return

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template_html = f.read()

    success_count = 0

    for district_name in districts:
        slug = get_slug(district_name)
        folder_path = BASE_DIR / slug
        index_path = folder_path / "index.html"

        if not index_path.exists():
            # Try original name case if slug doesn't work locally
            folder_path = BASE_DIR / district_name
            index_path = folder_path / "index.html"

        if index_path.exists():
            try:
                with open(index_path, "r", encoding="utf-8") as f:
                    content_soup = BeautifulSoup(f.read(), "html.parser")

                # 1. Clean up old boilerplate
                # Remove common outer structural elements if they exist
                for element in content_soup.find_all(['header', 'footer', 'nav']):
                    element.decompose()
                
                # If content is already in a column, extract just the inner stuff
                inner_container = content_soup.find("article", class_="content-column") or content_soup.find("div", class_="content-column")
                if inner_container:
                    raw_content = inner_container.decode_contents()
                else:
                    # Otherwise, get what's inside the body if present
                    raw_content = content_soup.body.decode_contents() if content_soup.body else content_soup.decode_contents()

                # 2. Re-parse with clean Template
                final_soup = BeautifulSoup(template_html, "html.parser")
                
                # Inject Main Content
                main_div = final_soup.find(id="main-content")
                if main_div:
                    main_div.append(BeautifulSoup(raw_content, "html.parser"))

                # 3. Handle Title & Meta Tags
                title_tag = final_soup.find("title")
                if title_tag:
                    title_tag.string = f"Educación Especial en {district_name} | Guía para Padres"

                # 4. District Resource Bar - Customize for this folder
                # We assume links are relative as per your template requirements
                # The template already has relative links: index.html, proceso-ard... etc.
                
                # 5. Write back to file
                with open(index_path, "w", encoding="utf-8") as f:
                    f.write(str(final_soup))
                
                print(f"✅ Deployed: {district_name}")
                success_count += 1

            except Exception as e:
                print(f"❌ Failed {district_name}: {e}")
        else:
            # Uncomment for debugging missing folders
            # print(f"⚠️ Folder not found: {slug}")
            pass

    print(f"\n🎉 Finished! Updated {success_count} index files.")

if __name__ == "__main__":
    main()