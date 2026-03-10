import requests
import xml.etree.ElementTree as ET

SITEMAP = "sitemap.xml"

headers = {
    "User-Agent": "Mozilla/5.0 (LinkCheckerBot)"
}

def get_urls_from_sitemap(file):
    tree = ET.parse(file)
    root = tree.getroot()

    urls = []
    for url in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        loc = url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
        urls.append(loc)

    return urls


def check_links(urls):
    broken = []

    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=10)

            if r.status_code != 200:
                print(f"⚠️ {url} -> {r.status_code}")
                broken.append((url, r.status_code))
            else:
                print(f"✅ {url}")

        except Exception as e:
            print(f"❌ {url} -> ERROR {e}")
            broken.append((url, "error"))

    return broken


urls = get_urls_from_sitemap(SITEMAP)
print(f"\nChecking {len(urls)} URLs\n")

broken_links = check_links(urls)

print("\nBroken Links:")
for link in broken_links:
    print(link)