"""
Quick Setup & Validation Script
================================
This script helps you prepare everything before running the formatters.
It checks dependencies, paths, and creates necessary files.

Usage:
    python setup_and_validate.py
"""

import os
import sys
import subprocess


def check_python_version():
    """Check if Python version is 3.7 or higher."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (need 3.7+)")
        return False


def check_beautifulsoup():
    """Check if BeautifulSoup4 is installed."""
    print("Checking BeautifulSoup4...")
    try:
        import bs4
        print(f"  ✓ BeautifulSoup4 {bs4.__version__}")
        return True
    except ImportError:
        print("  ❌ BeautifulSoup4 not installed")
        return False


def install_beautifulsoup():
    """Install BeautifulSoup4."""
    print("\nInstalling BeautifulSoup4...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
        print("  ✓ BeautifulSoup4 installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("  ❌ Failed to install BeautifulSoup4")
        print("     Try manually: pip install beautifulsoup4")
        return False


def check_directory(path):
    """Check if a directory exists."""
    if os.path.exists(path) and os.path.isdir(path):
        return True
    return False


def check_file(path):
    """Check if a file exists."""
    if os.path.exists(path) and os.path.isfile(path):
        return True
    return False


def setup_wizard():
    """Interactive setup wizard."""
    print("=" * 70)
    print("Spanish District Files - Setup & Validation")
    print("=" * 70)
    print()
    
    # Step 1: Check Python
    print("STEP 1: Checking Python")
    print("-" * 70)
    if not check_python_version():
        print("\n❌ Please upgrade Python to 3.7 or higher")
        print("   Download from: https://www.python.org/downloads/")
        return False
    print()
    
    # Step 2: Check/Install BeautifulSoup
    print("STEP 2: Checking Dependencies")
    print("-" * 70)
    if not check_beautifulsoup():
        response = input("\nDo you want to install BeautifulSoup4 now? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            if not install_beautifulsoup():
                return False
        else:
            print("❌ BeautifulSoup4 is required. Install it with: pip install beautifulsoup4")
            return False
    print()
    
    # Step 3: Get directory path
    print("STEP 3: Locating Your Files")
    print("-" * 70)
    
    default_path = r"\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts"
    print(f"Default path: {default_path}")
    
    use_default = input("Use this path? (yes/no): ")
    
    if use_default.lower() in ['yes', 'y']:
        base_dir = default_path
    else:
        base_dir = input("Enter the full path to your es-districts folder: ")
    
    print(f"\nChecking: {base_dir}")
    if not check_directory(base_dir):
        print(f"  ❌ Directory not found: {base_dir}")
        print("     Please check the path and try again")
        return False
    else:
        print(f"  ✓ Directory found")
    print()
    
    # Step 4: Check for template
    print("STEP 4: Checking Template File")
    print("-" * 70)
    template_path = os.path.join(base_dir, 'template.html')
    
    if check_file(template_path):
        print(f"  ✓ Template found: template.html")
    else:
        print(f"  ❌ Template not found: template.html")
        print(f"\n  You need to create the template file:")
        print(f"  1. Save your template HTML (como-solicitar-una-evaluacion-fie-en-fort-worth-isd.html)")
        print(f"  2. Rename it to: template.html")
        print(f"  3. Place it at: {template_path}")
        print()
        
        create_placeholder = input("Create a placeholder template.html file? (yes/no): ")
        if create_placeholder.lower() in ['yes', 'y']:
            try:
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write("""<!DOCTYPE html>
<html lang="es">
<head>
    <title>PLACEHOLDER - Replace with your actual template</title>
</head>
<body>
    <h1>Fort Worth ISD</h1>
    <p>This is a placeholder. Replace with your actual template content.</p>
</body>
</html>""")
                print(f"  ✓ Placeholder created at: {template_path}")
                print(f"  ⚠️  IMPORTANT: Replace this with your actual template!")
            except Exception as e:
                print(f"  ❌ Could not create placeholder: {e}")
        return False
    print()
    
    # Step 5: Count files
    print("STEP 5: Analyzing Files")
    print("-" * 70)
    
    html_count = 0
    index_count = 0
    subpage_count = 0
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html'):
                html_count += 1
                if 'index' in file.lower():
                    index_count += 1
                else:
                    subpage_count += 1
    
    print(f"Total HTML files: {html_count}")
    print(f"  • Index pages: {index_count}")
    print(f"  • Sub-pages: {subpage_count}")
    print()
    
    if html_count == 0:
        print("  ❌ No HTML files found!")
        print("     Check that your files are in district subdirectories")
        return False
    elif html_count < 50:
        print(f"  ⚠️  Only {html_count} files found. Expected ~125.")
        proceed = input("     Proceed anyway? (yes/no): ")
        if proceed.lower() not in ['yes', 'y']:
            return False
    else:
        print("  ✓ File count looks good")
    print()
    
    # Step 6: Update script configurations
    print("STEP 6: Updating Script Paths")
    print("-" * 70)
    
    scripts_to_update = [
        'format_spanish_subpages.py',
        'format_spanish_index_pages.py',
        'analyze_files.py'
    ]
    
    print("Updating paths in scripts...")
    
    for script in scripts_to_update:
        if os.path.exists(script):
            try:
                with open(script, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Update BASE_DIR
                content = content.replace(
                    'BASE_DIR = r"\\Users\\elisa\\OneDrive\\Documents\\texas-special-ed-site\\es-districts"',
                    f'BASE_DIR = r"{base_dir}"'
                )
                
                # Update TEMPLATE_PATH
                template_full_path = os.path.join(base_dir, 'template.html')
                content = content.replace(
                    'TEMPLATE_PATH = r"\\Users\\elisa\\OneDrive\\Documents\\texas-special-ed-site\\es-districts\\template.html"',
                    f'TEMPLATE_PATH = r"{template_full_path}"'
                )
                
                # Write back
                with open(script, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"  ✓ {script}")
            except Exception as e:
                print(f"  ❌ {script}: {e}")
        else:
            print(f"  ⚠️  {script} not found")
    
    print()
    
    # Final summary
    print("=" * 70)
    print("✅ SETUP COMPLETE!")
    print("=" * 70)
    print()
    print("Next Steps:")
    print("1. Run: python analyze_files.py")
    print("   (Review what files you have)")
    print()
    print("2. Run: python format_spanish_subpages.py")
    print(f"   (Format {subpage_count} sub-pages)")
    print()
    print("3. Run: python format_spanish_index_pages.py")
    print(f"   (Format {index_count} index pages)")
    print()
    print("⚠️  IMPORTANT: Backups will be created automatically (.backup files)")
    print()
    
    return True


def main():
    """Main execution function."""
    success = setup_wizard()
    
    if not success:
        print()
        print("=" * 70)
        print("❌ Setup incomplete. Please address the issues above and try again.")
        print("=" * 70)
    
    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()