r"""
Analyze Batch File - Separate English and Spanish Content
===========================================================
This script analyzes your batch file and shows you what you have
vs. what you need for complete English and Spanish sets.

Usage:
    python analyze_and_separate_batch.py
"""

import json
import os
from collections import defaultdict

# Path to batch file
BATCH_FILE = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\msgbatch_01MGmmvhTMRMVyLZDNVYkqGe_results.jsonl"


def analyze_batch(batch_path):
    """Analyze what's in the batch file."""
    
    print("=" * 70)
    print("Batch File Analysis")
    print("=" * 70)
    print()
    
    if not os.path.exists(batch_path):
        print(f"❌ Error: Batch file not found: {batch_path}")
        return
    
    # Track what we have
    districts = defaultdict(lambda: {'english': [], 'spanish': []})
    
    # Page types we expect (5 total per district)
    expected_page_types = {
        'index',
        'evaluation-child-find', 
        'ard-process-guide',
        'grievance-dispute-resolution',
        'como-solicitar-una-evaluacion-fie'
    }
    
    # Process each line
    with open(batch_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                custom_id = data.get('custom_id', '')
                
                # Extract district and page type
                parts = custom_id.split('_', 1)
                if len(parts) != 2:
                    continue
                
                district_slug = parts[0]
                page_type = parts[1]
                
                # Check if result succeeded
                result = data.get('result', {})
                if result.get('type') != 'succeeded':
                    continue
                
                # Determine language based on page type
                if 'como-solicitar' in page_type:
                    districts[district_slug]['spanish'].append(page_type)
                else:
                    districts[district_slug]['english'].append(page_type)
                    
            except Exception as e:
                continue
    
    # Summary
    print(f"📊 CURRENT INVENTORY")
    print("-" * 70)
    print(f"Total districts found: {len(districts)}")
    print()
    
    # Count pages by language
    total_english = sum(len(d['english']) for d in districts.values())
    total_spanish = sum(len(d['spanish']) for d in districts.values())
    
    print(f"English pages: {total_english}")
    print(f"Spanish pages: {total_spanish}")
    print(f"Total pages: {total_english + total_spanish}")
    print()
    
    # Analyze completeness
    print("=" * 70)
    print("📋 COMPLETENESS ANALYSIS")
    print("=" * 70)
    print()
    
    complete_english = 0
    complete_spanish = 0
    partial_districts = []
    
    for district, pages in sorted(districts.items()):
        english_count = len(pages['english'])
        spanish_count = len(pages['spanish'])
        
        # Check if complete (4 English OR 5 total pages)
        # English set is complete if it has index, evaluation, ard, grievance
        english_complete = english_count == 4
        # Spanish set would be complete if it had all 5 page types in Spanish
        spanish_complete = spanish_count == 5
        
        if english_complete:
            complete_english += 1
        if spanish_complete:
            complete_spanish += 1
        
        if not english_complete or not spanish_complete:
            partial_districts.append({
                'district': district,
                'english': english_count,
                'spanish': spanish_count
            })
    
    print(f"Districts with COMPLETE English set (4 pages): {complete_english}")
    print(f"Districts with COMPLETE Spanish set (5 pages): {complete_spanish}")
    print()
    
    # Show what's missing
    print("=" * 70)
    print("🔍 WHAT YOU HAVE vs. WHAT YOU NEED")
    print("=" * 70)
    print()
    
    print("For COMPLETE bilingual site, each district needs:")
    print("  English set: 5 pages (index, evaluation, ard, grievance, como-solicitar)")
    print("  Spanish set: 5 pages (index, evaluation, ard, grievance, como-solicitar)")
    print()
    
    print("What you HAVE:")
    print(f"  ✓ {complete_english} districts with 4 English pages")
    print(f"  ✓ {len(districts)} districts with 1 Spanish page (como-solicitar)")
    print()
    
    print("What you NEED to create:")
    print(f"  • English 'como-solicitar' page for {complete_english} districts")
    print(f"  • Spanish versions of 4 page types for {len(districts)} districts")
    print(f"    - Spanish index")
    print(f"    - Spanish evaluation-child-find")
    print(f"    - Spanish ard-process-guide")
    print(f"    - Spanish grievance-dispute-resolution")
    print()
    
    # Detailed breakdown
    print("=" * 70)
    print("📑 DETAILED BREAKDOWN (first 10 districts)")
    print("=" * 70)
    print()
    
    for i, (district, pages) in enumerate(sorted(districts.items())[:10], 1):
        print(f"{i}. {district.upper()}")
        print(f"   English pages ({len(pages['english'])}): {', '.join(sorted(pages['english']))}")
        print(f"   Spanish pages ({len(pages['spanish'])}): {', '.join(sorted(pages['spanish']))}")
        print()
    
    if len(districts) > 10:
        print(f"   ... and {len(districts) - 10} more districts")
        print()
    
    # Recommendations
    print("=" * 70)
    print("💡 RECOMMENDATIONS")
    print("=" * 70)
    print()
    
    print("STEP 1: Extract what you have")
    print("  Run: python extract_existing_batch.py")
    print("  This will separate:")
    print(f"    • {total_english} English pages → /districts/")
    print(f"    • {total_spanish} Spanish pages → /es-districts/")
    print()
    
    print("STEP 2: Generate missing content")
    print("  You'll need to create:")
    print(f"    • {complete_english} English 'como-solicitar' pages")
    print(f"    • {len(districts) * 4} Spanish pages (4 types × {len(districts)} districts)")
    print()
    
    print("STEP 3: Options for generating missing content")
    print("  A) Use Claude API batch mode again (recommended)")
    print("  B) Use the formatting scripts on translated content")
    print("  C) Use Claude.ai to generate them one by one")
    print()


def main():
    """Main execution."""
    analyze_batch(BATCH_FILE)
    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()