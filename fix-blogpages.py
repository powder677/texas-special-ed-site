import os
import re
from bs4 import BeautifulSoup, NavigableString

def process_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 1. Clean up the stray <html><p>=======</p></html> at the end of files
    html_content = re.sub(r'<html>\s*<p>\s*=======\s*</p>\s*</html>', '', html_content)

    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 2. Fix the missing "container" class on <main> tags
    main_tag = soup.find('main')
    if main_tag:
        classes = main_tag.get('class', [])
        if isinstance(classes, str):
            classes = [classes]
            
        if 'container' not in classes:
            classes.append('container')
            main_tag['class'] = classes
    else:
        # Fix for what-is-fie.html which is missing the <main> tag completely
        grid = soup.find('div', class_='page-grid')
        if grid and grid.parent and grid.parent.name == 'div' and 'container' in grid.parent.get('class', []):
            grid.parent.name = 'main'
            # Ensure it has the flex style to match other pages
            style = grid.parent.get('style', '')
            if 'flex:1' not in style.replace(' ', ''):
                grid.parent['style'] = (style + '; flex:1').strip(';')

    # 3. Wrap naked text inside the blog articles with <p> tags
    articles = soup.find_all('article', class_='blog-content')
    for article in articles:
        # Iterate over a copy of the contents so we can modify the tree safely
        for element in list(article.contents):
            # Check if the element is a free-floating text node
            if isinstance(element, NavigableString):
                text = element.string.strip()
                if text:
                    # Split by double newlines to separate paragraphs properly
                    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                    
                    for p_text in paragraphs:
                        new_p = soup.new_tag('p')
                        new_p.string = p_text
                        element.insert_before(new_p)
                    
                    # Remove the original naked text node
                    element.extract()

    # Save the repaired HTML back to the file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))
        
    print(f"✅ Repaired: {os.path.basename(filepath)}")

def main():
    # Set this to your folder path, '.' means the current directory
    directory = '.' 
    
    html_files_found = False
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            html_files_found = True
            filepath = os.path.join(directory, filename)
            process_html_file(filepath)
            
    if not html_files_found:
        print("No HTML files found in the directory.")
    else:
        print("All HTML files processed successfully!")

if __name__ == '__main__':
    main()