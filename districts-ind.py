import os
import re
from bs4 import BeautifulSoup

# The path to your districts folder
base_dir = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"
index_path = os.path.join(base_dir, "index.html")

# The master database of known district enrollments and regions
KNOWN_DATA = {
    "brownsville-isd": {"enrollment": 36140, "region": "South Texas"},
    "hallsville-isd": {"enrollment": 24602, "region": "East Texas"},
    "pearland-isd": {"enrollment": 20862, "region": "Houston"},
    "galena-park-isd": {"enrollment": 20862, "region": "Houston"},
    "southwest-isd": {"enrollment": 14833, "region": "San Antonio"},
    "eagle-pass-isd": {"enrollment": 13820, "region": "South Texas"},
    "fort-stockton-isd": {"enrollment": 13480, "region": "West Texas"},
    "cleveland-isd": {"enrollment": 12513, "region": "Houston"},
    "roscoe-collegiate-isd": {"enrollment": 12256, "region": "West Texas"},
    "deer-park-isd": {"enrollment": 12165, "region": "Houston"},
    "frenship-isd": {"enrollment": 11770, "region": "West Texas"},
    "canyon-isd": {"enrollment": 11565, "region": "Panhandle"},
    "duncanville-isd": {"enrollment": 11562, "region": "DFW"},
    "midlothian-isd": {"enrollment": 11356, "region": "DFW"},
    "waxahachie-isd": {"enrollment": 11196, "region": "DFW"},
    "brazosport-isd": {"enrollment": 11169, "region": "Houston"},
    "boerne-isd": {"enrollment": 11101, "region": "San Antonio"},
    "huntsville-isd": {"enrollment": 10960, "region": "East Texas"},
    "sheldon-isd": {"enrollment": 10946, "region": "Houston"},
    "harlandale-isd": {"enrollment": 10835, "region": "San Antonio"},
    "hutto-isd": {"enrollment": 10688, "region": "Austin"},
    "los-fresnos-cisd": {"enrollment": 10357, "region": "South Texas"},
    "manor-isd": {"enrollment": 9961, "region": "Austin"},
    "new-braunfels-isd": {"enrollment": 9893, "region": "San Antonio"},
    "sharyland-isd": {"enrollment": 9844, "region": "South Texas"},
    "liberty-hill-isd": {"enrollment": 9836, "region": "Austin"},
    "san-felipe-del-rio-cisd": {"enrollment": 9767, "region": "South Texas"},
    "medina-valley-isd": {"enrollment": 9638, "region": "San Antonio"},
    "willis-isd": {"enrollment": 9313, "region": "Houston"},
    "dripping-springs-isd": {"enrollment": 8712, "region": "Austin"},
    "aledo-isd": {"enrollment": 8430, "region": "DFW"},
    "edgewood-isd": {"enrollment": 8384, "region": "San Antonio"},
    "carroll-isd": {"enrollment": 8105, "region": "DFW"},
    "port-arthur-isd": {"enrollment": 8041, "region": "Southeast Texas"},
    "lubbock-cooper-isd": {"enrollment": 8030, "region": "West Texas"},
    "weatherford-isd": {"enrollment": 8023, "region": "DFW"},
    "granbury-isd": {"enrollment": 7962, "region": "DFW"},
    "barbers-hill-isd": {"enrollment": 7875, "region": "Houston"},
    "azle-isd": {"enrollment": 7304, "region": "DFW"},
    "angleton-isd": {"enrollment": 7105, "region": "Houston"},
    "la-porte-isd": {"enrollment": 7099, "region": "Houston"},
    "highland-park-isd": {"enrollment": 7073, "region": "DFW"},
    "south-san-antonio-isd": {"enrollment": 7001, "region": "San Antonio"},
    "crandall-isd": {"enrollment": 6922, "region": "DFW"},
    "cleburne-isd": {"enrollment": 6877, "region": "DFW"},
    "lufkin-isd": {"enrollment": 6865, "region": "East Texas"},
    "white-settlement-isd": {"enrollment": 6831, "region": "DFW"},
    "lancaster-isd": {"enrollment": 6822, "region": "DFW"},
    "lockhart-isd": {"enrollment": 6753, "region": "Austin"},
    "red-oak-isd": {"enrollment": 6696, "region": "DFW"},
    "ennis-isd": {"enrollment": 6646, "region": "DFW"},
    "cedar-hill-isd": {"enrollment": 6253, "region": "DFW"},
    "argyle-isd": {"enrollment": 6166, "region": "DFW"},
    "anna-isd": {"enrollment": 6038, "region": "DFW"},
    "joshua-isd": {"enrollment": 6026, "region": "DFW"},
    "roma-isd": {"enrollment": 6019, "region": "South Texas"},
    "corsicana-isd": {"enrollment": 5998, "region": "DFW"},
    "galveston-isd": {"enrollment": 5982, "region": "Houston"},
    "elgin-isd": {"enrollment": 5959, "region": "Austin"},
    "nacogdoches-isd": {"enrollment": 5766, "region": "East Texas"},
    "canutillo-isd": {"enrollment": 5747, "region": "El Paso"},
    "southside-isd": {"enrollment": 5740, "region": "San Antonio"},
    "splendora-isd": {"enrollment": 5687, "region": "Houston"},
    "dayton-isd": {"enrollment": 5675, "region": "Houston"},
    "flour-bluff-isd": {"enrollment": 5559, "region": "Coastal Bend"},
    "desoto-isd": {"enrollment": 5389, "region": "DFW"},
    "port-neches-groves-isd": {"enrollment": 5349, "region": "Southeast Texas"},
    "celina-isd": {"enrollment": 5324, "region": "DFW"},
    "nederland-isd": {"enrollment": 5317, "region": "Southeast Texas"},
    "community-isd": {"enrollment": 5271, "region": "DFW"},
    "greenville-isd": {"enrollment": 5218, "region": "DFW"},
    "mount-pleasant-isd": {"enrollment": 5153, "region": "East Texas"},
    "gregory-portland-isd": {"enrollment": 5024, "region": "Coastal Bend"},
    "everman-isd": {"enrollment": 5018, "region": "DFW"},
    "denison-isd": {"enrollment": 4977, "region": "North Texas"},
    "terrell-isd": {"enrollment": 4932, "region": "DFW"},
    "brenham-isd": {"enrollment": 4872, "region": "Central Texas"},
    "alamo-heights-isd": {"enrollment": 4749, "region": "San Antonio"},
    "jacksonville-isd": {"enrollment": 4700, "region": "East Texas"},
    "marshall-isd": {"enrollment": 4681, "region": "East Texas"},
    "whitehouse-isd": {"enrollment": 4676, "region": "East Texas"},
    "south-texas-isd": {"enrollment": 4639, "region": "South Texas"},
    "lindale-isd": {"enrollment": 4606, "region": "East Texas"},
    "kerrville-isd": {"enrollment": 4600, "region": "San Antonio"},
    "aubrey-isd": {"enrollment": 4480, "region": "DFW"},
    "pine-tree-isd": {"enrollment": 4439, "region": "East Texas"},
    "dumas-isd": {"enrollment": 4381, "region": "Panhandle"},
    "kaufman-isd": {"enrollment": 4356, "region": "DFW"},
    "alice-isd": {"enrollment": 4297, "region": "South Texas"},
    "somerset-isd": {"enrollment": 4259, "region": "San Antonio"},
    "valley-view-isd": {"enrollment": 4250, "region": "DFW"},
    "sulphur-springs-isd": {"enrollment": 4216, "region": "East Texas"},
    "andrews-isd": {"enrollment": 4209, "region": "West Texas"},
    "springtown-isd": {"enrollment": 4188, "region": "DFW"},
    "vidor-isd": {"enrollment": 4165, "region": "Southeast Texas"},
    "jarrell-isd": {"enrollment": 4157, "region": "Austin"},
    "lumberton-isd": {"enrollment": 4108, "region": "Southeast Texas"},
    "edcouch-elsa-isd": {"enrollment": 4083, "region": "South Texas"},
    "plainview-isd": {"enrollment": 4077, "region": "Panhandle"},
    "floresville-isd": {"enrollment": 4062, "region": "San Antonio"},
    "uvalde-cisd": {"enrollment": 4019, "region": "South Texas"},
    "livingston-isd": {"enrollment": 4016, "region": "East Texas"},
    "marble-falls-isd": {"enrollment": 4001, "region": "Austin"},
    "mercedes-isd": {"enrollment": 3970, "region": "South Texas"},
    "hereford-isd": {"enrollment": 3964, "region": "Panhandle"},
    "mabank-isd": {"enrollment": 3961, "region": "East Texas"},
    "lovejoy-isd": {"enrollment": 3959, "region": "DFW"},
    "castleberry-isd": {"enrollment": 3851, "region": "DFW"},
    "paris-isd": {"enrollment": 3832, "region": "East Texas"},
    "alvarado-isd": {"enrollment": 3788, "region": "DFW"},
    "decatur-isd": {"enrollment": 3786, "region": "DFW"},
    "chapel-hill-isd": {"enrollment": 3777, "region": "East Texas"},
    "calallen-isd": {"enrollment": 3745, "region": "Coastal Bend"},
    "lake-dallas-isd": {"enrollment": 3717, "region": "DFW"},
    "needville-isd": {"enrollment": 3650, "region": "Houston"},
    "huffman-isd": {"enrollment": 3646, "region": "Houston"},
    "lampasas-isd": {"enrollment": 3640, "region": "Central Texas"},
    "stephenville-isd": {"enrollment": 3578, "region": "Central Texas"},
    "tuloso-midway-isd": {"enrollment": 3566, "region": "Coastal Bend"},
    "la-vernia-isd": {"enrollment": 3563, "region": "San Antonio"},
    "kilgore-isd": {"enrollment": 3537, "region": "East Texas"},
    "calhoun-county-isd": {"enrollment": 3514, "region": "Coastal Bend"},
    "bay-city-isd": {"enrollment": 3473, "region": "Houston"},
    "pleasanton-isd": {"enrollment": 3406, "region": "San Antonio"},
    "brownwood-isd": {"enrollment": 3393, "region": "Central Texas"},
    "big-spring-isd": {"enrollment": 3376, "region": "West Texas"},
    "greenwood-isd": {"enrollment": 3373, "region": "West Texas"},
    "little-cypress-mauriceville-cisd": {"enrollment": 3320, "region": "Southeast Texas"},
    "mineral-wells-isd": {"enrollment": 3303, "region": "DFW"},
    "zapata-county-isd": {"enrollment": 3290, "region": "South Texas"},
    "el-campo-isd": {"enrollment": 3279, "region": "Houston"},
    "lake-worth-isd": {"enrollment": 3249, "region": "DFW"},
    "henderson-isd": {"enrollment": 3245, "region": "East Texas"},
    "burnet-cisd": {"enrollment": 3209, "region": "Austin"},
    "godley-isd": {"enrollment": 3195, "region": "DFW"},
    "bridge-city-isd": {"enrollment": 3157, "region": "Southeast Texas"},
    "pampa-isd": {"enrollment": 3141, "region": "Panhandle"},
    "navasota-isd": {"enrollment": 3117, "region": "Central Texas"},
    "gainesville-isd": {"enrollment": 3111, "region": "North Texas"},
    "sealy-isd": {"enrollment": 3109, "region": "Houston"},
    "seminole-isd": {"enrollment": 3089, "region": "West Texas"},
    "caddo-mills-isd": {"enrollment": 3073, "region": "DFW"},
    "beeville-isd": {"enrollment": 3033, "region": "Coastal Bend"},
    "burkburnett-isd": {"enrollment": 3030, "region": "North Texas"},
    "ferris-isd": {"enrollment": 3010, "region": "DFW"},
    "palestine-isd": {"enrollment": 2995, "region": "East Texas"},
    "gilmer-isd": {"enrollment": 2946, "region": "East Texas"},
    "china-spring-isd": {"enrollment": 2943, "region": "Central Texas"},
    "quinlan-isd": {"enrollment": 2936, "region": "DFW"},
    "taylor-isd": {"enrollment": 2930, "region": "Austin"},
    "pecos-barstow-toyah-isd": {"enrollment": 2919, "region": "West Texas"},
    "la-vega-isd": {"enrollment": 2897, "region": "Central Texas"},
    "sanger-isd": {"enrollment": 2880, "region": "DFW"},
    "fredericksburg-isd": {"enrollment": 2876, "region": "Central Texas"},
    "columbia-brazoria-isd": {"enrollment": 2871, "region": "Houston"},
    "athens-isd": {"enrollment": 2846, "region": "East Texas"},
    "bullard-isd": {"enrollment": 2835, "region": "East Texas"},
    "hudson-isd": {"enrollment": 2777, "region": "East Texas"},
    "hidalgo-isd": {"enrollment": 2771, "region": "South Texas"},
    "rockport-fulton-isd": {"enrollment": 2766, "region": "Coastal Bend"},
    "hardin-jefferson-isd": {"enrollment": 2762, "region": "Southeast Texas"},
    "san-elizario-isd": {"enrollment": 2755, "region": "El Paso"},
    "kennedale-isd": {"enrollment": 2754, "region": "DFW"},
    "royal-isd": {"enrollment": 2728, "region": "Houston"},
    "wills-point-isd": {"enrollment": 2716, "region": "East Texas"},
    "navarro-isd": {"enrollment": 2702, "region": "San Antonio"},
    "gatesville-isd": {"enrollment": 2668, "region": "Central Texas"},
    "la-feria-isd": {"enrollment": 2667, "region": "South Texas"},
    "carthage-isd": {"enrollment": 2637, "region": "East Texas"},
    "van-alstyne-isd": {"enrollment": 2612, "region": "North Texas"},
    "west-orange-cove-cisd": {"enrollment": 2592, "region": "Southeast Texas"},
    "silsbee-isd": {"enrollment": 2588, "region": "Southeast Texas"},
    "levelland-isd": {"enrollment": 2575, "region": "West Texas"},
    "gonzales-isd": {"enrollment": 2557, "region": "Central Texas"},
    "krum-isd": {"enrollment": 2542, "region": "DFW"},
    "kingsville-isd": {"enrollment": 2534, "region": "South Texas"},
    "wimberley-isd": {"enrollment": 2508, "region": "Austin"},
    "brownsboro-isd": {"enrollment": 2451, "region": "East Texas"},
    "liberty-isd": {"enrollment": 2438, "region": "Southeast Texas"},
    "robstown-isd": {"enrollment": 2411, "region": "Coastal Bend"},
    "farmersville-isd": {"enrollment": 2397, "region": "DFW"},
    "north-lamar-isd": {"enrollment": 2395, "region": "East Texas"},
    "robinson-isd": {"enrollment": 2378, "region": "Central Texas"},
    
    # Original Top Districts
    "houston-isd": {"enrollment": 175777, "region": "Houston"},
    "dallas-isd": {"enrollment": 139046, "region": "Dallas"},
    "cypress-fairbanks-isd": {"enrollment": 118010, "region": "Houston"},
    "northside-isd": {"enrollment": 101095, "region": "San Antonio"},
    "katy-isd": {"enrollment": 96119, "region": "Houston"},
    "fort-bend-isd": {"enrollment": 80985, "region": "Houston"},
    "idea-public-schools": {"enrollment": 80246, "region": "Statewide"},
    "conroe-isd": {"enrollment": 73380, "region": "Houston"},
    "austin-isd": {"enrollment": 72830, "region": "Austin"},
    "fort-worth-isd": {"enrollment": 71060, "region": "Fort Worth"},
    "frisco-isd": {"enrollment": 67327, "region": "DFW"},
    "aldine-isd": {"enrollment": 57844, "region": "Houston"},
    "north-east-isd": {"enrollment": 57374, "region": "San Antonio"},
    "arlington-isd": {"enrollment": 54750, "region": "DFW"},
    "klein-isd": {"enrollment": 54082, "region": "Houston"},
    "garland-isd": {"enrollment": 51659, "region": "DFW"},
    "el-paso-isd": {"enrollment": 49139, "region": "El Paso"},
    "lewisville-isd": {"enrollment": 48440, "region": "DFW"},
    "plano-isd": {"enrollment": 47899, "region": "DFW"},
    "pasadena-isd": {"enrollment": 47486, "region": "Houston"},
    "humble-isd": {"enrollment": 47460, "region": "Houston"},
    "socorro-isd": {"enrollment": 47020, "region": "El Paso"},
    "round-rock-isd": {"enrollment": 46197, "region": "Austin"},
    "san-antonio-isd": {"enrollment": 44670, "region": "San Antonio"},
    "killeen-isd": {"enrollment": 43760, "region": "Central Texas"},
    "lamar-cisd": {"enrollment": 43620, "region": "Houston"},
    "leander-isd": {"enrollment": 41920, "region": "Austin"},
    "united-isd": {"enrollment": 40950, "region": "Laredo"},
    "clear-creek-isd": {"enrollment": 40150, "region": "Houston"},
    "harmony-public-schools": {"enrollment": 38000, "region": "Statewide"},
    "mesquite-isd": {"enrollment": 37900, "region": "DFW"},
    "richardson-isd": {"enrollment": 36880, "region": "DFW"},
    "alief-isd": {"enrollment": 39474, "region": "Houston"},
    "mansfield-isd": {"enrollment": 35660, "region": "Fort Worth"},
    "ysleta-isd": {"enrollment": 34918, "region": "El Paso"},
    "denton-isd": {"enrollment": 33670, "region": "DFW"},
    "ector-county-isd": {"enrollment": 33560, "region": "West Texas"},
    "spring-isd": {"enrollment": 33490, "region": "Houston"},
    "spring-branch-isd": {"enrollment": 33260, "region": "Houston"},
    "corpus-christi-isd": {"enrollment": 33053, "region": "Coastal Bend"},
    "keller-isd": {"enrollment": 33030, "region": "Fort Worth"},
    "irving-isd": {"enrollment": 30580, "region": "DFW"},
    "prosper-isd": {"enrollment": 30860, "region": "DFW"},
    "pharr-san-juan-alamo-isd": {"enrollment": 30008, "region": "Rio Grande Valley"},
    "alvin-isd": {"enrollment": 29320, "region": "Houston"},
    "amarillo-isd": {"enrollment": 29729, "region": "Panhandle"},
    "northwest-isd": {"enrollment": 29660, "region": "Fort Worth"},
    "comal-isd": {"enrollment": 29480, "region": "San Antonio"},
    "edinburg-cisd": {"enrollment": 29450, "region": "Rio Grande Valley"},
    "midland-isd": {"enrollment": 28340, "region": "West Texas"},
    "judson-isd": {"enrollment": 25670, "region": "San Antonio"},
    "pflugerville-isd": {"enrollment": 25480, "region": "Austin"},
    "carrollton-farmers-branch-isd": {"enrollment": 25120, "region": "DFW"},
    "lubbock-isd": {"enrollment": 24329, "region": "South Plains"},
    "hays-cisd": {"enrollment": 23450, "region": "Austin"},
    "la-joya-isd": {"enrollment": 23998, "region": "Rio Grande Valley"},
    "eagle-mountain-saginaw-isd": {"enrollment": 23870, "region": "Fort Worth"},
    "goose-creek-cisd": {"enrollment": 23810, "region": "Houston"},
    "mckinney-isd": {"enrollment": 23320, "region": "DFW"},
    "tomball-isd": {"enrollment": 22530, "region": "Houston"},
    "birdville-isd": {"enrollment": 22180, "region": "Fort Worth"},
    "allen-isd": {"enrollment": 21790, "region": "DFW"},
    "hurst-euless-bedford-isd": {"enrollment": 21890, "region": "Fort Worth"},
    "laredo-isd": {"enrollment": 20592, "region": "Laredo"},
    "mcallen-isd": {"enrollment": 20095, "region": "Rio Grande Valley"},
    "wylie-isd": {"enrollment": 19530, "region": "DFW"},
    "new-caney-isd": {"enrollment": 18540, "region": "Houston"},
    "rockwall-isd": {"enrollment": 18650, "region": "DFW"},
    "harlingen-cisd": {"enrollment": 17160, "region": "Rio Grande Valley"},
    "crowley-isd": {"enrollment": 16920, "region": "Fort Worth"},
    "forney-isd": {"enrollment": 16840, "region": "DFW"},
    "weslaco-isd": {"enrollment": 16040, "region": "Rio Grande Valley"},
    "bryan-isd": {"enrollment": 15530, "region": "Central Texas"},
    "schertz-cibolo-universal-city-isd": {"enrollment": 15590, "region": "San Antonio"},
    "magnolia-isd": {"enrollment": 14580, "region": "Houston"},
    "belton-isd": {"enrollment": 14140, "region": "Central Texas"},
    "abilene-isd": {"enrollment": 14890, "region": "West Texas"},
    "college-station-isd": {"enrollment": 14080, "region": "Central Texas"},
    "mission-cisd": {"enrollment": 14020, "region": "Rio Grande Valley"},
    "donna-isd": {"enrollment": 13240, "region": "Rio Grande Valley"},
    "coppell-isd": {"enrollment": 13180, "region": "DFW"},
    "grapevine-colleyville-isd": {"enrollment": 13120, "region": "DFW"},
    "san-angelo-isd": {"enrollment": 13120, "region": "West Texas"},
    "bastrop-isd": {"enrollment": 12940, "region": "Austin"},
    "wichita-falls-isd": {"enrollment": 12980, "region": "North Texas"},
    "dickinson-isd": {"enrollment": 12340, "region": "Houston"},
    "burleson-isd": {"enrollment": 12740, "region": "Fort Worth"},
    "lake-travis-isd": {"enrollment": 11640, "region": "Austin"},
    "east-central-isd": {"enrollment": 11040, "region": "San Antonio"},
    "del-valle-isd": {"enrollment": 11240, "region": "Austin"},
    "clint-isd": {"enrollment": 10340, "region": "El Paso"},
    "sherman-isd": {"enrollment": 10650, "region": "North Texas"},
    "georgetown-isd": {"enrollment": 13670, "region": "Austin"},
    "montgomery-isd": {"enrollment": 9870, "region": "Houston"},
    "royse-city-isd": {"enrollment": 9430, "region": "DFW"},
    "rio-grande-city-grulla-isd": {"enrollment": 9480, "region": "Rio Grande Valley"},
    "san-benito-cisd": {"enrollment": 9120, "region": "Rio Grande Valley"},
    "waller-isd": {"enrollment": 9120, "region": "Houston"},
    "little-elm-isd": {"enrollment": 8920, "region": "DFW"},
    "midway-isd": {"enrollment": 8420, "region": "Central Texas"},
    "temple-isd": {"enrollment": 8340, "region": "Central Texas"},
    "san-marcos-cisd": {"enrollment": 8210, "region": "Austin"},
    "longview-isd": {"enrollment": 8050, "region": "East Texas"},
    "eanes-isd": {"enrollment": 7890, "region": "Austin"},
    "texas-city-isd": {"enrollment": 7870, "region": "Houston"},
    "seguin-isd": {"enrollment": 7140, "region": "San Antonio"},
    "texarkana-isd": {"enrollment": 7230, "region": "East Texas"},
    "copperas-cove-isd": {"enrollment": 7980, "region": "Central Texas"},
    "crosby-isd": {"enrollment": 6680, "region": "Houston"},
    "princeton-isd": {"enrollment": 8720, "region": "DFW"},
    "melissa-isd": {"enrollment": 6250, "region": "DFW"},
    "friendswood-isd": {"enrollment": 5890, "region": "Houston"},
    "channelview-isd": {"enrollment": 9320, "region": "Houston"},
    "victoria-isd": {"enrollment": 12890, "region": "Coastal Bend"},
    "waco-isd": {"enrollment": 14240, "region": "Central Texas"},
    "beaumont-isd": {"enrollment": 16520, "region": "Southeast Texas"},
    "tyler-isd": {"enrollment": 17890, "region": "East Texas"},
    "santa-fe-isd": {"enrollment": 4230, "region": "Houston"},
    "grand-prairie-isd": {"enrollment": 26638, "region": "DFW"}
}

# Mobile/Responsive CSS we are injecting into index.html
mobile_css = """
<style id="directory-mobile-enhancements">
/* ── DIRECTORY GRID & MOBILE ENHANCEMENTS ── */
#district-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px; padding: 20px 0; }
.district-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 24px; text-decoration: none; color: inherit; display: flex; flex-direction: column; transition: transform 0.2s, box-shadow 0.2s; }
.district-card:hover { transform: translateY(-4px); box-shadow: 0 12px 20px -5px rgba(0,0,0,0.1); border-color: #cbd5e1; }
.district-region { font-size: 0.75rem; color: #1a56db; text-transform: uppercase; font-weight: 800; letter-spacing: 0.05em; margin-bottom: 8px; }
.district-name { font-size: 1.35rem; font-family: 'Lora', serif; font-weight: 700; color: #0a2342; margin-bottom: 8px; line-height: 1.3; }
.district-enrollment { font-size: 0.95rem; color: #64748b; margin-bottom: 20px; flex-grow: 1; }
.district-link { color: #d4af37; font-weight: 800; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; }
.controls-bar { background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 30px; }
.controls-inner { display: flex; gap: 15px; flex-wrap: wrap; align-items: center; }
.search-wrap { flex-grow: 1; min-width: 250px; display: flex; align-items: center; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 0 15px; }
.search-wrap input { border: none; background: transparent; padding: 12px; width: 100%; outline: none; font-size: 16px; }
select { padding: 12px 15px; border: 1px solid #cbd5e1; border-radius: 6px; background: #f8fafc; font-size: 15px; outline: none; min-width: 150px; }
.result-count { font-weight: 600; color: #475569; margin-left: auto; }
.dir-stats { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: white; padding: 40px 20px; border-radius: 12px; margin: 30px 0; }
.dir-stats-inner { display: flex; justify-content: space-around; flex-wrap: wrap; gap: 20px; max-width: 900px; margin: 0 auto; text-align: center; }
.dir-stat { display: flex; flex-direction: column; font-size: 1.1rem; color: #cbd5e1; }
.dir-stat strong { font-size: 2.5rem; color: #fff; font-family: 'Lora', serif; line-height: 1; margin-bottom: 8px; }

/* Critical Mobile Stack Fixes */
@media (max-width: 768px) {
    .controls-inner { flex-direction: column; align-items: stretch; }
    .search-wrap { width: 100%; box-sizing: border-box; }
    select { width: 100%; }
    .result-count { margin-left: 0; text-align: center; padding-top: 10px; border-top: 1px solid #e2e8f0; }
    #district-grid { grid-template-columns: 1fr; }
    .dir-stats-inner { flex-direction: column; gap: 30px; }
}
</style>
"""

def process_index():
    if not os.path.exists(index_path):
        print(f"Index file not found at {index_path}")
        return

    # 1. READ ALL DIRECTORIES DYNAMICALLY
    actual_districts = []
    
    # Grab all folders in your directory
    folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
    
    for slug in folders:
        # Ignore things that clearly aren't districts
        if not (slug.endswith('-isd') or slug.endswith('-cisd') or 'schools' in slug):
            continue
            
        # Format "angleton-isd" -> "Angleton ISD"
        parts = slug.split('-')
        formatted_parts = []
        for p in parts:
            if p.lower() == 'isd':
                formatted_parts.append('ISD')
            elif p.lower() == 'cisd':
                formatted_parts.append('CISD')
            else:
                formatted_parts.append(p.capitalize())
        name = ' '.join(formatted_parts)
        
        # Pull data if we know it, otherwise set defaults
        data = KNOWN_DATA.get(slug, {"enrollment": 0, "region": "Texas"})
        actual_districts.append({
            "name": name,
            "enrollment": data["enrollment"],
            "region": data["region"]
        })

    # Sort the array by size
    actual_districts = sorted(actual_districts, key=lambda x: x['enrollment'], reverse=True)

    # 2. GENERATE JAVASCRIPT ARRAY
    js_lines = ["var DISTRICTS = ["]
    for d in actual_districts:
        js_lines.append(f'  {{ name: "{d["name"]}", enrollment: {d["enrollment"]}, region: "{d["region"]}" }},')
    js_lines.append("];")
    new_js_array = "\n".join(js_lines)

    # 3. PARSE HTML AND REPLACE
    with open(index_path, 'r', encoding='utf-8') as f:
        html_text = f.read()
        
    # Replace the JS Array via regex
    html_text = re.sub(r'var DISTRICTS = \[.*?\];', new_js_array, html_text, flags=re.DOTALL)
    
    # Update the "120 Districts" stats counter 
    html_text = re.sub(r'<strong>\d+</strong> Districts', f'<strong>{len(actual_districts)}</strong> Districts', html_text)

    # 4. INJECT THE MOBILE CSS
    soup = BeautifulSoup(html_text, 'html.parser')
    
    # Remove old version if running multiple times
    existing_style = soup.find('style', id='directory-mobile-enhancements')
    if existing_style:
        existing_style.decompose()
        
    head = soup.find('head')
    if head:
        style_tag = BeautifulSoup(mobile_css, 'html.parser')
        head.append(style_tag)
        
    # 5. SAVE CHANGES
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
        
    print(f"✅ Success! Updated index.html with {len(actual_districts)} districts and added mobile CSS.")

if __name__ == "__main__":
    process_index()