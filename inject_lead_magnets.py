import os
import re

# Mapping of blog post filenames to their highly contextual lead magnets
MAGNETS = {
    'special-ed-discipline-texas.html': {
        'title': 'Fighting a Discipline Issue or Suspension?',
        'text': 'Don\'t go into a Manifestation Determination Review (MDR) unprepared. Get our free Texas Behavior Defense Kit, including copy-paste email templates to hold the school accountable.',
        'link': '../download/bx-defense-5t1q.html',
        'button': 'Get the Free Behavior Kit'
    },
    'manifestation-determination.html': {
        'title': 'Is Your Child Facing Disciplinary Action?',
        'text': 'The MDR process is heavily stacked against parents. Protect your child\'s rights with our free Texas Behavior Defense Kit and proven email templates.',
        'link': '../download/bx-defense-5t1q.html',
        'button': 'Download the Defense Kit'
    },
    'ard-meeting-tips.html': {
        'title': 'Nervous About Your Upcoming ARD Meeting?',
        'text': 'Walk in with confidence. Get our comprehensive ARD Prep Toolkit, including step-by-step checklists and the exact questions you MUST ask.',
        'link': '../download/ard-prep-3n8w.html',
        'button': 'Get the Free ARD Prep Toolkit'
    },
    'what-is-an-ard-meeting.html': {
        'title': 'Attending Your First ARD Meeting?',
        'text': 'Don\'t get overwhelmed by the paperwork, acronyms, and educators. Download our free ARD Prep Toolkit to know exactly what to expect and how to prepare.',
        'link': '../download/ard-prep-3n8w.html',
        'button': 'Download the ARD Toolkit'
    },
    '10-questions-to-ask-at-ard-meeting.html': {
        'title': 'Ready to Take Control of Your ARD?',
        'text': 'Make sure you have all the tools you need. Download our free full ARD Prep Toolkit to keep the school accountable and secure the best IEP.',
        'link': '../download/ard-prep-3n8w.html',
        'button': 'Get the Free Toolkit'
    },
    'dyslexia-hb3928-changes.html': {
        'title': 'Confused by the New Texas Dyslexia Rules?',
        'text': 'HB 3928 changed everything. Make sure your child gets a full Special Education Evaluation (IEP), not just a 504 plan. Get our free Dyslexia Support Toolkit.',
        'link': '../download/dys-toolkit-7m2p.html',
        'button': 'Download the Dyslexia Toolkit'
    }
}

def inject_magnets():
    # Adjust this if your blog files are in a different root folder
    blog_dir = './blog'
    if not os.path.exists(blog_dir):
        print(f"❌ Could not find {blog_dir} directory.")
        return

    modified_count = 0

    for filename, magnet_data in MAGNETS.items():
        filepath = os.path.join(blog_dir, filename)
        
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if "UX FIX: Contextual Lead Magnet" in content:
            print(f"⚠️ Already injected in {filename}, skipping.")
            continue

        # Template for the high-contrast CRO box
        # Colors: Soft blue background, bold blue border, strong red CTA button for high conversion
        html_snippet = f"""
<div class="contextual-lead-magnet" style="background-color: #f4f8fc; border: 3px solid #004085; padding: 35px 25px; margin: 40px 0; border-radius: 8px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <h3 style="margin-top: 0; color: #004085; font-size: 24px; font-weight: 800; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">{magnet_data['title']}</h3>
    <p style="color: #333; font-size: 17px; line-height: 1.6; margin-bottom: 25px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin-left: auto; margin-right: auto;">{magnet_data['text']}</p>
    <a href="{magnet_data['link']}" style="background-color: #d9534f; color: white; padding: 15px 30px; text-decoration: none; font-weight: bold; font-size: 18px; border-radius: 6px; display: inline-block; box-shadow: 0 3px 6px rgba(217,83,79,0.4); text-transform: uppercase; letter-spacing: 0.5px;">{magnet_data['button']}</a>
</div>
"""
        
        # Smart Injection Logic: Find the middle of the article
        h2_tags = [m for m in re.finditer(r'<h2[^>]*>', content, re.IGNORECASE)]
        
        if len(h2_tags) >= 2:
            # Inject before the middle H2 tag
            middle_index = len(h2_tags) // 2
            insert_pos = h2_tags[middle_index].start()
            new_content = content[:insert_pos] + html_snippet + content[insert_pos:]
        else:
            # Fallback: split by paragraph tags and inject in the middle
            p_tags = [m for m in re.finditer(r'</p>', content, re.IGNORECASE)]
            if len(p_tags) >= 2:
                middle_index = len(p_tags) // 2
                insert_pos = p_tags[middle_index].end()
                new_content = content[:insert_pos] + html_snippet + content[insert_pos:]
            else:
                new_content = content
                
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            modified_count += 1
            print(f"✅ Injected mapped lead magnet into: {filename}")

    print(f"\n🎯 Lead Magnet Injection Complete. Modified {modified_count} blog posts.")

if __name__ == '__main__':
    inject_magnets()