import os
import difflib
import re

def main():
    # 1. Define the directory path where your folders are located
    base_dir = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts"

    # 2. Hardcoded list of proper district names
    proper_names = [
        'HOUSTON ISD', 'DALLAS ISD', 'CYPRESS-FAIRBANKS ISD', 'NORTHSIDE ISD', 'KATY ISD', 
        'FORT BEND ISD', 'CONROE ISD', 'AUSTIN ISD', 'FORT WORTH ISD', 'FRISCO ISD', 
        'NORTH EAST ISD', 'ALDINE ISD', 'ARLINGTON ISD', 'KLEIN ISD', 'GARLAND ISD', 
        'HUMBLE ISD', 'EL PASO ISD', 'LEWISVILLE ISD', 'ROUND ROCK ISD', 'LAMAR CISD', 
        'SOCORRO ISD', 'PLANO ISD', 'PASADENA ISD', 'SAN ANTONIO ISD', 'KILLEEN ISD', 
        'LEANDER ISD', 'UNITED ISD', 'CLEAR CREEK ISD', 'ALIEF ISD', 'MESQUITE ISD', 
        'RICHARDSON ISD', 'BROWNSVILLE ISD', 'MANSFIELD ISD', 'YSLETA ISD', 'ECTOR COUNTY ISD', 
        'SPRING ISD', 'EDINBURG CISD', 'DENTON ISD', 'CORPUS CHRISTI ISD', 'SPRING BRANCH ISD', 
        'NORTHWEST ISD', 'KELLER ISD', 'PROSPER ISD', 'IRVING ISD', 'ALVIN ISD', 
        'COMAL ISD', 'MIDLAND ISD', 'PHARR-SAN JUAN-ALAMO ISD', 'AMARILLO ISD', 'GRAND PRAIRIE ISD', 
        'PFLUGERVILLE ISD', 'WYLIE ISD', 'HALLSVILLE ISD', 'HAYS CISD', 'CARROLLTON-FARMERS BRANCH ISD', 
        'LUBBOCK ISD', 'GOOSE CREEK CISD', 'EAGLE MT-SAGINAW ISD', 'JUDSON ISD', 'MCKINNEY ISD', 
        'HURST-EULESS-BEDFORD ISD', 'LA JOYA ISD', 'TOMBALL ISD', 'BIRDVILLE ISD', 'PEARLAND ISD', 
        'GALENA PARK ISD', 'ALLEN ISD', 'MCALLEN ISD', 'NEW CANEY ISD', 'ROCKWALL ISD', 
        'LAREDO ISD', 'TYLER ISD', 'FORNEY ISD', 'CROWLEY ISD', 'HARLINGEN CISD', 
        'BEAUMONT ISD', 'BRYAN ISD', 'WESLACO ISD', 'SCHERTZ-CIBOLO-U CITY ISD', 'MAGNOLIA ISD', 
        'SOUTHWEST ISD', 'ABILENE ISD', 'COLLEGE STATION ISD', 'GEORGETOWN ISD', 'EAGLE PASS ISD', 
        'BELTON ISD', 'GRAPEVINE-COLLEYVILLE ISD', 'FORT STOCKTON ISD', 'WACO ISD', 'BASTROP ISD', 
        'COPPELL ISD', 'SAN ANGELO ISD', 'DONNA ISD', 'MISSION CISD', 'VICTORIA ISD', 
        'BURLESON ISD', 'WICHITA FALLS ISD', 'DICKINSON ISD', 'CLEVELAND ISD', 'ROSCOE COLLEGIATE ISD', 
        'DEER PARK ISD', 'FRENSHIP ISD', 'DEL VALLE ISD', 'CANYON ISD', 'DUNCANVILLE ISD', 
        'EAST CENTRAL ISD', 'MIDLOTHIAN ISD', 'WAXAHACHIE ISD', 'BRAZOSPORT ISD', 'BOERNE ISD', 
        'LAKE TRAVIS ISD', 'HUNTSVILLE ISD', 'SHELDON ISD', 'HARLANDALE ISD', 'HUTTO ISD', 
        'LOS FRESNOS CISD', 'CLINT ISD', 'ROYSE CITY ISD', 'MANOR ISD', 'PRINCETON ISD', 
        'WALLER ISD', 'NEW BRAUNFELS ISD', 'MONTGOMERY ISD', 'SHARYLAND ISD', 'LIBERTY HILL ISD', 
        'SAN FELIPE-DEL RIO CISD', 'MEDINA VALLEY ISD', 'CHANNELVIEW ISD', 'WILLIS ISD', 'SAN BENITO CISD', 
        'MIDWAY ISD', 'TEMPLE ISD', 'RIO GRANDE CITY GRULLA ISD', 'DRIPPING SPRINGS ISD', 'ALEDO ISD', 
        'EDGEWOOD ISD', 'SAN MARCOS CISD', 'LONGVIEW ISD', 'CARROLL ISD', 'PORT ARTHUR ISD', 
        'LITTLE ELM ISD', 'LUBBOCK-COOPER ISD', 'WEATHERFORD ISD', 'GRANBURY ISD', 'BARBERS HILL ISD', 
        'SHERMAN ISD', 'COPPERAS COVE ISD', 'MELISSA ISD', 'TEXAS CITY ISD', 'EANES ISD', 
        'AZLE ISD', 'SEGUIN ISD', 'TEXARKANA ISD', 'ANGLETON ISD', 'LA PORTE ISD', 
        'HIGHLAND PARK ISD', 'CROSBY ISD', 'SOUTH SAN ANTONIO ISD', 'CRANDALL ISD', 'CLEBURNE ISD', 
        'LUFKIN ISD', 'WHITE SETTLEMENT ISD', 'LANCASTER ISD', 'LOCKHART ISD', 'RED OAK ISD', 
        'ENNIS ISD', 'CEDAR HILL ISD', 'FRIENDSWOOD ISD', 'ARGYLE ISD', 'ANNA ISD', 
        'JOSHUA ISD', 'ROMA ISD', 'CORSICANA ISD', 'GALVESTON ISD', 'ELGIN ISD', 
        'NACOGDOCHES ISD', 'CANUTILLO ISD', 'SOUTHSIDE ISD', 'SPLENDORA ISD', 'DAYTON ISD', 
        'FLOUR BLUFF ISD', 'DESOTO ISD', 'PORT NECHES-GROVES ISD', 'CELINA ISD', 'NEDERLAND ISD', 
        'COMMUNITY ISD', 'GREENVILLE ISD', 'MOUNT PLEASANT ISD', 'GREGORY-PORTLAND ISD', 'EVERMAN ISD', 
        'DENISON ISD', 'TERRELL ISD', 'BRENHAM ISD', 'ALAMO HEIGHTS ISD', 'JACKSONVILLE ISD', 
        'MARSHALL ISD', 'WHITEHOUSE ISD', 'SOUTH TEXAS ISD', 'LINDALE ISD', 'KERRVILLE ISD', 
        'AUBREY ISD', 'PINE TREE ISD', 'DUMAS ISD', 'KAUFMAN ISD', 'SANTA FE ISD', 
        'ALICE ISD', 'SOMERSET ISD', 'VALLEY VIEW ISD', 'SULPHUR SPRINGS ISD', 'ANDREWS ISD', 
        'SPRINGTOWN ISD', 'VIDOR ISD', 'JARRELL ISD', 'LUMBERTON ISD', 'EDCOUCH-ELSA ISD', 
        'PLAINVIEW ISD', 'FLORESVILLE ISD', 'UVALDE CISD', 'LIVINGSTON ISD', 'MARBLE FALLS ISD', 
        'MERCEDES ISD', 'HEREFORD ISD', 'MABANK ISD', 'LOVEJOY ISD', 'CASTLEBERRY ISD', 
        'PARIS ISD', 'ALVARADO ISD', 'DECATUR ISD', 'CHAPEL HILL ISD', 'CALALLEN ISD', 
        'LAKE DALLAS ISD', 'NEEDVILLE ISD', 'HUFFMAN ISD', 'LAMPASAS ISD', 'STEPHENVILLE ISD', 
        'TULOSO-MIDWAY ISD', 'LA VERNIA ISD', 'KILGORE ISD', 'CALHOUN COUNTY ISD', 'BAY CITY ISD', 
        'PLEASANTON ISD', 'BROWNWOOD ISD', 'BIG SPRING ISD', 'GREENWOOD ISD', 'LITTLE CYPRESS-MAURICEVILLE CISD', 
        'MINERAL WELLS ISD', 'ZAPATA COUNTY ISD', 'EL CAMPO ISD', 'LAKE WORTH ISD', 'HENDERSON ISD', 
        'BURNET CISD', 'GODLEY ISD', 'BRIDGE CITY ISD', 'PAMPA ISD', 'NAVASOTA ISD', 
        'GAINESVILLE ISD', 'SEALY ISD', 'SEMINOLE ISD', 'CADDO MILLS ISD', 'BEEVILLE ISD', 
        'BURKBURNETT ISD', 'FERRIS ISD', 'PALESTINE ISD', 'GILMER ISD', 'CHINA SPRING ISD', 
        'QUINLAN ISD', 'TAYLOR ISD', 'PECOS-BARSTOW-TOYAH ISD', 'LA VEGA ISD', 'SANGER ISD', 
        'FREDERICKSBURG ISD', 'COLUMBIA-BRAZORIA ISD', 'ATHENS ISD', 'BULLARD ISD', 'HUDSON ISD', 
        'HIDALGO ISD', 'ROCKPORT-FULTON ISD', 'HARDIN-JEFFERSON ISD', 'SAN ELIZARIO ISD', 'KENNEDALE ISD', 
        'ROYAL ISD', 'WILLS POINT ISD', 'NAVARRO ISD', 'GATESVILLE ISD', 'LA FERIA ISD', 
        'CARTHAGE ISD', 'VAN ALSTYNE ISD', 'WEST ORANGE-COVE CISD', 'SILSBEE ISD', 'LEVELLAND ISD', 
        'GONZALES ISD', 'KRUM ISD', 'KINGSVILLE ISD', 'WIMBERLEY ISD', 'BROWNSBORO ISD', 
        'LIBERTY ISD', 'ROBSTOWN ISD', 'FARMERSVILLE ISD', 'NORTH LAMAR ISD', 'ROBINSON ISD'
    ]

    # 3. Helper function to normalize names for better matching
    def normalize(name):
        name = name.lower()
        # Remove common suffixes to match purely on the core name
        name = re.sub(r'\b(isd|cisd|county)\b', '', name)
        # Remove spaces, hyphens, and special characters
        name = re.sub(r'[^a-z0-9]', '', name)
        return name

    # Create a mapping of the "normalized" proper name back to the "Real Proper Name"
    name_mapping = {normalize(name): name for name in proper_names}

    # 4. Iterate through the items in the es-districts folder
    if not os.path.exists(base_dir):
        print(f"Could not find the directory at: {base_dir}")
        return

    print("Scanning directory and renaming folders...\n")
    
    for folder_name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder_name)
        
        # We only want to rename folders (directories)
        if os.path.isdir(folder_path):
            norm_folder = normalize(folder_name)
            
            # Check for an exact normalized match
            if norm_folder in name_mapping:
                best_match = name_mapping[norm_folder]
            else:
                # Fallback to fuzzy matching if the spelling is slightly off
                matches = difflib.get_close_matches(norm_folder, list(name_mapping.keys()), n=1, cutoff=0.75)
                if matches:
                    best_match = name_mapping[matches[0]]
                else:
                    best_match = None
                    
            # 5. Rename the folder if a match is found and it isn't already the proper name
            if best_match and best_match != folder_name:
                new_path = os.path.join(base_dir, best_match)
                try:
                    os.rename(folder_path, new_path)
                    print(f"✅ Renamed: '{folder_name}'  -->  '{best_match}'")
                except Exception as e:
                    print(f"❌ Error renaming '{folder_name}': {e}")
            elif not best_match:
                print(f"⚠️ Could not find a match for folder: '{folder_name}'")

if __name__ == "__main__":
    main()