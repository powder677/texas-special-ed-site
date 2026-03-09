"""
fix_all_redirects.py
====================
Writes 301 redirects to vercel.json for three known issues:

  1. what-is-fie rename (only districts that actually have the new file):
       /districts/{d}/what-is-fie  →  /districts/{d}/what-is-fie-{d}

  2. Dead districts → district directory:
       /districts/highland-park-isd(/.*)  →  /districts/
       /districts/lovejoy-isd(/.*)        →  /districts/
       /districts/carroll-isd(/.*)        →  /districts/

  3. Lamar rename (preserves sub-page):
       /districts/lamar-isd          →  /districts/lamar-cisd
       /districts/lamar-isd/(.*)     →  /districts/lamar-cisd/$1

USAGE
-----
  python fix_all_redirects.py \
    --dir "C:/Users/elisa/OneDrive/Documents/texas-special-ed-site" \
    --dry-run

  Remove --dry-run when ready to write.
"""

import json
import argparse
from pathlib import Path

DISTRICTS_DIR  = "districts"

DEAD_DISTRICTS = [
    "highland-park-isd",
    "lovejoy-isd",
    "carroll-isd",
]

RENAMED_DISTRICTS = {
    "lamar-isd": "lamar-cisd",
}


def find_fie_redirects(root: Path) -> list[dict]:
    """
    Scan every district folder. If it contains a what-is-fie-{district}
    file/folder, generate a redirect from the old what-is-fie slug.
    """
    redirects = []
    districts_path = root / DISTRICTS_DIR
    if not districts_path.exists():
        print(f"  ERROR: {districts_path} not found")
        return []

    for district_dir in sorted(districts_path.iterdir()):
        if not district_dir.is_dir():
            continue
        slug = district_dir.name

        # Look for the new file in either form:
        #   what-is-fie-{slug}/index.html  OR  what-is-fie-{slug}.html
        new_slug = f"what-is-fie-{slug}"
        has_new = (
            (district_dir / new_slug / "index.html").exists() or
            (district_dir / f"{new_slug}.html").exists()
        )
        # Only add redirect if new file exists AND old slug no longer exists
        old_slug = "what-is-fie"
        has_old = (
            (district_dir / old_slug / "index.html").exists() or
            (district_dir / f"{old_slug}.html").exists()
        )

        if has_new and not has_old:
            redirects.append({
                "source":      f"/districts/{slug}/what-is-fie",
                "destination": f"/districts/{slug}/what-is-fie-{slug}",
                "permanent":   True
            })

    return redirects


def build_dead_district_redirects() -> list[dict]:
    redirects = []
    for d in DEAD_DISTRICTS:
        # Redirect the index page
        redirects.append({
            "source":      f"/districts/{d}",
            "destination": "/districts/",
            "permanent":   True
        })
        # Redirect any sub-pages
        redirects.append({
            "source":      f"/districts/{d}/:path*",
            "destination": "/districts/",
            "permanent":   True
        })
    return redirects


def build_lamar_redirects() -> list[dict]:
    redirects = []
    for old, new in RENAMED_DISTRICTS.items():
        # Index page
        redirects.append({
            "source":      f"/districts/{old}",
            "destination": f"/districts/{new}",
            "permanent":   True
        })
        # Sub-pages — Vercel wildcard carries :path* through
        redirects.append({
            "source":      f"/districts/{old}/:path*",
            "destination": f"/districts/{new}/:path*",
            "permanent":   True
        })
    return redirects


def load_existing_vercel(root: Path) -> dict:
    vpath = root / "vercel.json"
    if vpath.exists():
        try:
            with open(vpath, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception as e:
            print(f"  ⚠️  Could not read vercel.json ({e}) — starting fresh")
    return {}


def write_vercel(root: Path, new_redirects: list[dict], dry_run: bool) -> int:
    config = load_existing_vercel(root)
    existing = config.get("redirects", [])
    existing_sources = {r.get("source") for r in existing}

    added, dupes = [], []
    for r in new_redirects:
        if r["source"] not in existing_sources:
            existing.append(r)
            added.append(r)
            existing_sources.add(r["source"])
        else:
            dupes.append(r["source"])

    config["redirects"] = existing

    if dry_run:
        print(f"\n  [DRY RUN] {len(added)} redirect(s) would be added")
        if dupes:
            print(f"  {len(dupes)} already exist (skipped)\n")
        for r in added:
            print(f"  {r['source']}")
            print(f"    → {r['destination']}")
        return len(added)

    vpath = root / "vercel.json"
    with open(vpath, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)
    print(f"\n  ✅ vercel.json updated — {len(added)} redirect(s) added")
    if dupes:
        print(f"  ⏭️  {len(dupes)} already existed (skipped)")
    print(f"  📄 {vpath}")
    return len(added)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir",     required=True, help="Root of your site")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.dir)
    if not root.exists():
        print(f"ERROR: Directory not found: {root}")
        exit(1)

    print(f"\n{'═'*60}")
    print(f"  Site : {root}")
    print(f"  Mode : {'DRY RUN' if args.dry_run else 'LIVE — will write vercel.json'}")
    print(f"{'═'*60}\n")

    # 1. what-is-fie renames (only where new file exists on disk)
    fie_redirects = find_fie_redirects(root)
    print(f"📋 what-is-fie districts found : {len(fie_redirects)}")

    # 2. Dead districts
    dead_redirects = build_dead_district_redirects()
    print(f"🗑️  Dead district redirects     : {len(dead_redirects)}")

    # 3. Lamar rename
    lamar_redirects = build_lamar_redirects()
    print(f"✏️  Lamar rename redirects      : {len(lamar_redirects)}")

    all_redirects = fie_redirects + dead_redirects + lamar_redirects
    print(f"\n   Total new redirects          : {len(all_redirects)}")

    write_vercel(root, all_redirects, dry_run=args.dry_run)

    if not args.dry_run:
        print("\nNext steps:")
        print("  1. Review vercel.json")
        print("  2. Deploy to Vercel")
        print("  3. In Google Search Console → Pages → Not found (404)")
        print("     click 'Validate Fix' once deployed\n")


if __name__ == "__main__":
    main()