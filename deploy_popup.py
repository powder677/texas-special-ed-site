# Newsletter Popup Deployment Script
# Auto-deploy newsletter popup to all HTML files

import os
import shutil
from datetime import datetime

PROJECT_PATH = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site"
BACKUP_FOLDER = os.path.join(PROJECT_PATH, "_backups_before_popup")

POPUP_CSS = """
    <!-- Newsletter Popup Styles -->
    <style>
        .newsletter-popup-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(10, 35, 66, 0.92);
            z-index: 9999;
            display: flex; align-items: center; justify-content: center;
            opacity: 0; visibility: hidden; 
            transition: opacity 0.4s ease, visibility 0.4s;
            backdrop-filter: blur(6px);
        }
        .newsletter-popup-overlay.show { opacity: 1; visibility: visible; }
        
        .newsletter-popup-content {
            background: #fff; width: 92%; max-width: 520px;
            border-radius: 16px; position: relative;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.3);
            transform: translateY(30px) scale(0.9); 
            transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
            overflow: hidden;
        }
        .newsletter-popup-overlay.show .newsletter-popup-content { 
            transform: translateY(0) scale(1); 
        }
        
        .newsletter-popup-close {
            position: absolute; top: 16px; right: 16px;
            background: rgba(255,255,255,0.15); 
            border: none; width: 36px; height: 36px;
            border-radius: 50%; color: #fff; font-size: 24px; 
            cursor: pointer; z-index: 10;
            display: flex; align-items: center; justify-content: center;
            transition: all 0.2s;
            font-weight: 300;
            line-height: 1;
        }
        .newsletter-popup-close:hover { 
            background: rgba(255,255,255,0.25); 
            transform: rotate(90deg);
        }
        
        .newsletter-popup-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
            padding: 48px 36px 36px; 
            text-align: center; 
            position: relative;
            overflow: hidden;
        }
        .newsletter-popup-header::before {
            content: ''; position: absolute; top: -50%; right: -20%;
            width: 300px; height: 300px;
            background: radial-gradient(circle, rgba(212, 175, 55, 0.15) 0%, transparent 70%);
            pointer-events: none;
        }
        
        .newsletter-popup-icon {
            width: 64px; height: 64px;
            background: rgba(212, 175, 55, 0.2);
            border: 3px solid rgba(212, 175, 55, 0.4);
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 32px;
            margin: 0 auto 20px;
            position: relative;
        }
        
        .newsletter-popup-tag {
            color: #d4af37; font-size: 12px; font-weight: 700; 
            text-transform: uppercase; letter-spacing: 0.12em; 
            display: inline-block; margin-bottom: 12px;
            background: rgba(212, 175, 55, 0.15); 
            padding: 6px 16px; border-radius: 20px;
        }
        
        .newsletter-popup-header h3 { 
            font-family: 'Lora', serif; 
            font-size: 28px; 
            color: #fff; 
            margin: 0; 
            line-height: 1.25;
            position: relative;
        }
        
        .newsletter-popup-body { 
            padding: 36px; 
            background: #fff;
        }
        
        .newsletter-popup-benefits {
            list-style: none;
            margin: 0 0 28px 0;
            padding: 0;
        }
        .newsletter-popup-benefits li {
            padding: 12px 0 12px 36px;
            position: relative;
            font-size: 15px;
            color: #475569;
            line-height: 1.5;
            border-bottom: 1px solid #f1f5f9;
        }
        .newsletter-popup-benefits li:last-child {
            border-bottom: none;
        }
        .newsletter-popup-benefits li::before {
            content: '✓';
            position: absolute;
            left: 0;
            color: #10b981;
            font-weight: 700;
            font-size: 18px;
        }
        
        .newsletter-popup-input {
            width: 100%; 
            padding: 16px 20px; 
            border: 2px solid #e2e8f0;
            border-radius: 10px; 
            font-size: 16px; 
            font-family: 'DM Sans', -apple-system, sans-serif;
            margin-bottom: 12px; 
            transition: all 0.3s ease;
            color: #0a2342;
        }
        .newsletter-popup-input:focus { 
            outline: none; 
            border-color: #1a56db;
            box-shadow: 0 0 0 3px rgba(26, 86, 219, 0.1);
        }
        
        .newsletter-popup-btn {
            width: 100%; 
            padding: 16px 24px; 
            background: #d4af37; 
            color: #0a2342;
            border: none; 
            border-radius: 10px; 
            font-size: 16px; 
            font-weight: 700;
            font-family: 'DM Sans', -apple-system, sans-serif; 
            cursor: pointer; 
            transition: all 0.3s ease;
        }
        .newsletter-popup-btn:hover { 
            background: #c29d2e; 
            transform: translateY(-2px); 
            box-shadow: 0 8px 20px rgba(212, 175, 55, 0.3);
        }
        
        .newsletter-popup-privacy { 
            font-size: 13px !important; 
            color: #94a3b8 !important; 
            margin: 0 !important; 
            text-align: center;
            line-height: 1.5;
        }
        
        .newsletter-popup-success {
            padding: 36px;
            text-align: center;
            display: none;
        }
        .newsletter-popup-success.show {
            display: block;
        }
        .newsletter-popup-success-icon {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 24px;
            font-size: 40px;
            color: #fff;
        }
        .newsletter-popup-success h3 {
            font-family: 'Lora', serif;
            font-size: 24px;
            color: #0a2342;
            margin-bottom: 12px;
        }
        .newsletter-popup-success p {
            color: #64748b;
            font-size: 15px;
            line-height: 1.6;
            margin-bottom: 24px;
        }
        
        @media (max-width: 640px) {
            .newsletter-popup-header { padding: 40px 24px 28px; }
            .newsletter-popup-header h3 { font-size: 24px; }
            .newsletter-popup-body { padding: 28px 24px; }
            .newsletter-popup-benefits li { font-size: 14px; }
        }
    </style>
"""

POPUP_HTML_AND_JS = """
    <!-- Newsletter Popup -->
    <div id="newsletterPopup" class="newsletter-popup-overlay">
        <div class="newsletter-popup-content">
            <button class="newsletter-popup-close" onclick="closeNewsletterPopup()" aria-label="Close">×</button>
            
            <div id="popupForm">
                <div class="newsletter-popup-header">
                    <div class="newsletter-popup-icon">📧</div>
                    <span class="newsletter-popup-tag">Free Weekly Newsletter</span>
                    <h3>Get Texas Special Ed Guidance Every Week</h3>
                </div>
                
                <div class="newsletter-popup-body">
                    <ul class="newsletter-popup-benefits">
                        <li>Real case studies from Texas parents who won their ARD meetings</li>
                        <li>District-specific timelines and escalation strategies</li>
                        <li>Policy updates from TEA that affect your rights</li>
                        <li>Letter templates and meeting prep checklists</li>
                    </ul>
                    
                    <form id="newsletterForm" class="newsletter-popup-form" onsubmit="handleNewsletterSubmit(event)">
                        <input 
                            type="email" 
                            id="popupEmail"
                            class="newsletter-popup-input"
                            placeholder="Enter your email address" 
                            required
                        >
                        <button type="submit" class="newsletter-popup-btn" id="submitBtn">
                            Join 8,200+ Texas Parents →
                        </button>
                    </form>
                    
                    <p class="newsletter-popup-privacy">
                        Free forever. Weekly emails. Unsubscribe anytime.<br>
                        We respect your privacy and never share your email.
                    </p>
                </div>
            </div>
            
            <div id="popupSuccess" class="newsletter-popup-success">
                <div class="newsletter-popup-success-icon">✓</div>
                <h3>You're on the list!</h3>
                <p>Check your inbox for a confirmation email. Your first newsletter arrives this Thursday with strategies from parents who successfully navigated the Texas special education system.</p>
                <button class="newsletter-popup-btn" onclick="closeNewsletterPopup()">
                    Continue Reading
                </button>
            </div>
        </div>
    </div>

    <script>
        const POPUP_CONFIG = {
            delaySeconds: 10,
            sessionStorageKey: 'txSpecEdPopupShown',
        };

        document.addEventListener("DOMContentLoaded", function() {
            if (sessionStorage.getItem(POPUP_CONFIG.sessionStorageKey)) {
                return;
            }
            
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('nopopup') === 'true') {
                return;
            }
            
            setTimeout(function() {
                const popup = document.getElementById('newsletterPopup');
                if (popup) {
                    popup.classList.add('show');
                    sessionStorage.setItem(POPUP_CONFIG.sessionStorageKey, 'true');
                }
            }, POPUP_CONFIG.delaySeconds * 1000);
        });

        function closeNewsletterPopup() {
            const popup = document.getElementById('newsletterPopup');
            if (popup) {
                popup.classList.remove('show');
            }
        }

        if (document.getElementById('newsletterPopup')) {
            document.getElementById('newsletterPopup').addEventListener('click', function(e) {
                if (e.target === this) {
                    closeNewsletterPopup();
                }
            });
        }

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeNewsletterPopup();
            }
        });

        async function handleNewsletterSubmit(event) {
            event.preventDefault();
            
            const emailInput = document.getElementById('popupEmail');
            const submitBtn = document.getElementById('submitBtn');
            const email = emailInput.value.trim().toLowerCase();
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Subscribing...';
            
            try {
                await saveNewsletterSignup(email);
                
                document.getElementById('popupForm').style.display = 'none';
                document.getElementById('popupSuccess').classList.add('show');
                
            } catch (error) {
                console.error('Newsletter signup error:', error);
                alert('Something went wrong. Please try again or email us directly.');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Join 8,200+ Texas Parents →';
            }
        }

        async function saveNewsletterSignup(email) {
            const pageUrl = window.location.pathname;
            const pageTitle = document.title;
            
            const districtMatch = pageUrl.match(/\/districts\/([^\/]+)/);
            const district = districtMatch ? districtMatch[1] : null;
            
            const signupData = {
                email: email,
                source: 'newsletter_popup',
                page_url: pageUrl,
                page_title: pageTitle,
                district: district,
                timestamp: new Date().toISOString(),
                subscribed: true,
                tags: ['newsletter_popup', district].filter(Boolean)
            };
            
            const response = await fetch('/api/newsletter-signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(signupData)
            });
            
            if (!response.ok) {
                throw new Error('API error');
            }
            
            return await response.json();
        }
    </script>
"""

def create_backup(filepath):
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)
    
    rel_path = os.path.relpath(filepath, PROJECT_PATH)
    backup_path = os.path.join(BACKUP_FOLDER, rel_path)
    
    backup_dir = os.path.dirname(backup_path)
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    shutil.copy2(filepath, backup_path)
    return backup_path

def has_popup(content):
    return 'newsletterPopup' in content or 'newsletter-popup-overlay' in content

def inject_popup(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if has_popup(content):
        return "SKIP", "Already has popup"
    
    if '</head>' not in content or '</body>' not in content:
        return "SKIP", "Not a valid HTML file"
    
    backup_path = create_backup(filepath)
    
    try:
        content = content.replace('</head>', POPUP_CSS + '\n</head>')
        content = content.replace('</body>', POPUP_HTML_AND_JS + '\n</body>')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return "SUCCESS", "Popup added"
        
    except Exception as e:
        shutil.copy2(backup_path, filepath)
        return "ERROR", str(e)

def find_html_files(root_path):
    html_files = []
    
    for root, dirs, files in os.walk(root_path):
        if '_backups_' in root:
            continue
        
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    return html_files

def main():
    print("=" * 80)
    print("NEWSLETTER POPUP DEPLOYMENT")
    print("=" * 80)
    print("\nProject path:", PROJECT_PATH)
    print("Backup folder:", BACKUP_FOLDER)
    print("\nSearching for HTML files...")
    
    html_files = find_html_files(PROJECT_PATH)
    
    if not html_files:
        print("\nERROR: No HTML files found!")
        print("Check if this is the right path:", PROJECT_PATH)
        return
    
    print("\nFound", len(html_files), "HTML files")
    print("\nStarting deployment...\n")
    
    results = {"SUCCESS": [], "SKIP": [], "ERROR": []}
    
    for i, filepath in enumerate(html_files, 1):
        rel_path = os.path.relpath(filepath, PROJECT_PATH)
        status, message = inject_popup(filepath)
        
        results[status].append((rel_path, message))
        
        if status == "SUCCESS":
            print("[{}/{}] SUCCESS: {}".format(i, len(html_files), rel_path))
        elif status == "SKIP":
            print("[{}/{}] SKIP: {}".format(i, len(html_files), rel_path))
        else:
            print("[{}/{}] ERROR: {} - {}".format(i, len(html_files), rel_path, message))
    
    print("\n" + "=" * 80)
    print("DEPLOYMENT SUMMARY")
    print("=" * 80)
    print("\nSuccessfully added popup:", len(results['SUCCESS']), "files")
    print("Skipped:", len(results['SKIP']), "files")
    print("Errors:", len(results['ERROR']), "files")
    
    if results['SUCCESS']:
        print("\nSUCCESSFULLY MODIFIED FILES:")
        for rel_path, message in results['SUCCESS'][:10]:
            print("  -", rel_path)
        if len(results['SUCCESS']) > 10:
            print("  ... and", len(results['SUCCESS']) - 10, "more")
    
    if results['ERROR']:
        print("\nERRORS:")
        for rel_path, message in results['ERROR']:
            print("  -", rel_path, ":", message)
    
    print("\nAll original files backed up to:", BACKUP_FOLDER)
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n1. Test on one page (wait 10 seconds for popup)")
    print("2. Add backend endpoint to app.py")
    print("3. Deploy to production")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    if not os.path.exists(PROJECT_PATH):
        print("\nERROR: Project path does not exist!")
        print(PROJECT_PATH)
        print("\nUpdate PROJECT_PATH in this script.")
    else:
        main()