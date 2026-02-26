import os
import csv

def extract_to_csv():
    source_dir = './districts_updated'
    output_csv = 'extracted_resources.csv'
    
    if not os.path.exists(source_dir):
        print(f"❌ Source directory '{source_dir}' not found.")
        return

    extracted_data = []
    
    for subdir, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(subdir, file)
                
                # Smart Slug Detection
                if " partners.html" in file.lower():
                    slug = file.lower().replace(" partners.html", "").strip()
                elif "partners.html" in file.lower():
                    slug = os.path.basename(subdir).lower().strip()
                else:
                    slug = os.path.basename(subdir).lower().strip()
                    
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # ROBUST EXTRACTION LOGIC
                # Instead of exact tags, we look for keywords to avoid spacing issues
                start_hint = content.find('free-resources-section')
                end_hint = content.find('END FREE RESOURCES SECTION')
                
                if start_hint != -1 and end_hint != -1:
                    # Back up to the actual <div tag
                    start_idx = content.rfind('<div', 0, start_hint)
                    # Move forward to the close of the comment -->
                    end_idx = content.find('-->', end_hint)
                    
                    if start_idx != -1 and end_idx != -1:
                        # +3 to include the final '-->'
                        block = content[start_idx:end_idx + 3] 
                        extracted_data.append([slug, block])
                        
                        # Print confirmation to the terminal so we KNOW it grabbed code
                        print(f"✅ Extracted {len(block)} characters of code for: {slug}")
                    
    # Write to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['DistrictSlug', 'HTMLBlock'])
        writer.writerows(extracted_data)
        
    print(f"\n🎯 EXTRACTION COMPLETE: Successfully stored heavy code blocks for {len(extracted_data)} districts.")

if __name__ == '__main__':
    extract_to_csv()