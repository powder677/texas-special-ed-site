import re
import json

def fix_invisible_links(html_file_path):
    # 1. Read the file
    with open(html_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 2. Extract the JS data (The "DISTRICTS" array)
    # We look for var DISTRICTS = [ ... ];
    pattern = r"var DISTRICTS = (\[.*?\]);"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("Error: Could not find the DISTRICTS variable in the script.")
        return

    # Parse the JS array into a Python list
    # We need to make the JS object syntax valid JSON (add quotes to keys)
    js_array_str = match.group(1)
    
    # Simple regex to quote unquoted keys (e.g. name: "Houston") -> ("name": "Houston")
    json_ready_str = re.sub(r'(\w+):', r'"\1":', js_array_str)
    # Remove trailing commas which JS allows but JSON hates
    json_ready_str = re.sub(r',\s*]', ']', json_ready_str)
    
    try:
        districts = json.loads(json_ready_str)
        print(f"Found {len(districts)} districts in your script.")
    except json.JSONDecodeError as e:
        print(f"Error parsing district data: {e}")
        return

    # 3. Generate the Static HTML Cards
    # We match the exact CSS classes you are already using
    static_html_cards = []
    
    for d in districts:
        # Create the URL slug (e.g. "Houston ISD" -> "houston-isd")
        slug = d['name'].lower().replace(' ', '-').replace('.', '')
        url = f"/districts/{slug}/index.html"
        
        card = f"""
        <div class="district-card" data-region="{d['region']}" data-enrollment="{d['enrollment']}" data-name="{d['name']}">
          <span class="district-region">{d['region']}</span>
          <h2 class="district-name">{d['name']}</h2>
          <div class="district-enrollment">{d['enrollment']:,} Students</div>
          <a href="{url}" class="district-link">View Resources &rarr;</a>
        </div>"""
        static_html_cards.append(card)

    final_grid_html = '\n'.join(static_html_cards)

    # 4. Inject into the HTML
    # We look for <div id="district-grid">...</div> and replace the inside
    new_content = re.sub(
        r'(<div id="district-grid">)(.*?)(</div>)',
        f'\\1\n{final_grid_html}\n\\3',
        content,
        flags=re.DOTALL
    )

    # 5. Save the fixed file
    output_filename = "index_fixed.html"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print(f"Success! Created '{output_filename}' with {len(districts)} static links.")
    print("Upload this file to your server to replace your current index.html.")

# Run the function
# fix_invisible_links("index.html")