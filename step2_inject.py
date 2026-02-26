import os
import csv

def inject_from_csv():
    input_csv = 'extracted_resources.csv'
    target_base = './districts'
    
    if not os.path.exists(input_csv):
        print(f"❌ {input_csv} not found. Please run step1_extract.py first.")
        return
        
    injected_count = 0
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            slug = row['DistrictSlug']
            html_block = row['HTMLBlock']
            
            # Target the live partner page
            target_file = os.path.join(target_base, slug, 'partners.html')
            
            # Fallback for flat file architecture
            if not os.path.exists(target_file):
                target_file = os.path.join(target_base, f"{slug} partners.html")
                
            if os.path.exists(target_file):
                with open(target_file, 'r', encoding='utf-8') as target:
                    content = target.read()
                    
                # Prevent duplicate injections
                if '<div class="free-resources-section">' in content:
                    continue
                    
                # Find the safest place to drop the code (Bottom of page, above footer)
                inject_idx = content.find('</main>')
                if inject_idx == -1:
                    inject_idx = content.find('<footer')
                if inject_idx == -1:
                    inject_idx = content.find('</body>')
                    
                if inject_idx != -1:
                    # Inject the code
                    new_content = content[:inject_idx] + "\n" + html_block + "\n\n" + content[inject_idx:]
                    
                    with open(target_file, 'w', encoding='utf-8') as target:
                        target.write(new_content)
                    injected_count += 1
                    
    print(f"✅ INJECTION COMPLETE: Safely pushed resources into {injected_count} live partner pages.")

if __name__ == '__main__':
    inject_from_csv()