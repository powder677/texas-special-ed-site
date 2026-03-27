import os

# Set this to your actual folder path
DIRECTORY = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"

# The CSS is the same for both languages
CSS_TO_INJECT = """
<!-- IEP ANALYZER BANNER STYLES (Safely scoped) -->
<style>
      #iep-banner {
         background: #0f1f3d;
         position: relative;
         overflow: hidden;
         font-family: 'DM Sans', sans-serif;
         border-radius: 12px;
         margin: 30px 0;
         box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15);
      }
      #iep-banner * { box-sizing: border-box; }
      #iep-banner::before {
         content: '';
         position: absolute;
         inset: 0;
         background:
            radial-gradient(ellipse 70% 80% at 0% 50%,  #1e3a6e55 0%, transparent 60%),
            radial-gradient(ellipse 50% 60% at 100% 50%, #c9820a1a 0%, transparent 55%),
            repeating-linear-gradient(0deg, transparent, transparent 80px, rgba(255,255,255,.012) 80px, rgba(255,255,255,.012) 81px);
         pointer-events: none;
      }
      #iep-banner .star-bg {
         position: absolute; right: -30px; top: 50%; transform: translateY(-50%);
         font-size: 320px; color: rgba(255,255,255,.025); line-height: 1;
         pointer-events: none; user-select: none; font-family: serif;
      }
      .banner-inner {
         position: relative; z-index: 1; display: flex; align-items: center;
         justify-content: space-between; gap: 32px; padding: 48px 56px;
         max-width: 1200px; margin: 0 auto;
      }
      .banner-text { flex: 1; min-width: 0; }
      .banner-eyebrow {
         display: inline-flex; align-items: center; gap: 8px; font-size: 11px;
         font-weight: 600; letter-spacing: .18em; text-transform: uppercase;
         color: #f0a52a; background: rgba(201,130,10,.12);
         border: 1px solid rgba(201,130,10,.3); border-radius: 100px;
         padding: 5px 13px; margin-bottom: 18px;
      }
      .banner-eyebrow .dot {
         width: 6px; height: 6px; background: #f0a52a; border-radius: 50%;
         flex-shrink: 0; animation: blink 2s ease infinite;
      }
      @keyframes blink { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: .4; transform: scale(.7); } }
      .banner-headline {
         font-family: 'Playfair Display', serif; font-size: clamp(26px, 3.5vw, 40px);
         font-weight: 700; color: #fff; line-height: 1.15; letter-spacing: -.01em;
         margin-bottom: 14px; margin-top: 0;
      }
      .banner-headline em { color: #f0a52a; font-style: normal; }
      .banner-sub {
         font-family: 'Lora', serif; font-style: italic; color: rgba(255,255,255,.55);
         font-size: 16px; line-height: 1.7; max-width: 480px; margin-bottom: 28px;
      }
      .trust-row { display: flex; align-items: center; flex-wrap: wrap; gap: 20px; }
      .trust-item { display: flex; align-items: center; gap: 7px; font-size: 12.5px; color: rgba(255,255,255,.5); }
      .trust-item .check {
         width: 16px; height: 16px; background: rgba(201,130,10,.25);
         border: 1px solid rgba(201,130,10,.4); border-radius: 50%;
         display: flex; align-items: center; justify-content: center;
         font-size: 9px; color: #f0a52a; flex-shrink: 0;
      }
      .banner-cta-card {
         flex-shrink: 0; width: 360px; background: rgba(255,255,255,.06);
         border: 1px solid rgba(255,255,255,.1); border-radius: 16px;
         padding: 28px 24px; text-align: center;
         backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px);
      }
      .cta-card-label {
         font-size: 11px; font-weight: 600; letter-spacing: .12em;
         text-transform: uppercase; color: #60a5fa; margin-bottom: 6px;
      }
      .cta-card-desc {
         font-size: 14px; color: #fff; line-height: 1.5; margin-bottom: 16px; text-align: left;
      }
      .banner-feature-list { list-style: none; padding: 0; margin: 16px 0 24px; }
      .banner-feature-list li {
         display: flex; align-items: flex-start; gap: 10px; margin-bottom: 12px;
         font-size: 14.5px; color: rgba(255,255,255,.9); line-height: 1.5;
      }
      .banner-feature-list .check { color: #f0a52a; font-weight: bold; flex-shrink: 0; }
      .cta-feature-list { list-style: none; padding: 0; margin: 0 0 24px; text-align: left; }
      .cta-feature-list li {
         display: flex; align-items: flex-start; gap: 8px; margin-bottom: 10px;
         font-size: 13.5px; color: rgba(255,255,255,.85); line-height: 1.4;
      }
      .cta-feature-list .check { color: #10b981; font-weight: bold; flex-shrink: 0; }
      .cta-add-on {
         font-size: 12.5px; color: #f0a52a; font-style: italic; margin-top: 12px; margin-bottom: 16px; line-height: 1.4;
      }
      .cta-btn {
         display: block; width: 100%; padding: 14px 20px;
         background: linear-gradient(135deg, #c0392b 0%, #96291f 100%);
         color: #fff !important; font-family: 'DM Sans', sans-serif; font-size: 15px;
         font-weight: 600; letter-spacing: .02em; text-decoration: none;
         border-radius: 10px; text-align: center; box-shadow: 0 4px 20px rgba(192,57,43,.45);
         transition: transform .15s, box-shadow .15s; cursor: pointer; border: none;
         margin-bottom: 12px; position: relative; overflow: hidden;
      }
      .cta-btn::after {
         content: ''; position: absolute; top: 0; left: -100%; width: 60%; height: 100%;
         background: linear-gradient(90deg, transparent, rgba(255,255,255,.12), transparent);
         transition: left .4s ease;
      }
      .cta-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(192,57,43,.55); }
      .cta-btn:hover::after { left: 150%; }
      .cta-btn:active { transform: translateY(0); }
      .cta-btn-arrow { display: inline-block; transition: transform .2s; margin-left: 6px; }
      .cta-btn:hover .cta-btn-arrow { transform: translateX(4px); }
      .cta-fine-print { font-size: 11px; color: rgba(255,255,255,.3); line-height: 1.5; margin-bottom: 0; }
      .iep-rule { display: flex; align-items: center; gap: 10px; margin-bottom: 28px; }
      .iep-rule::before { content: ''; height: 1px; width: 40px; background: linear-gradient(to right, rgba(201,130,10,.4), transparent); }
      .iep-rule-diamond { width: 5px; height: 5px; background: #c9820a; transform: rotate(45deg); flex-shrink: 0; }
      .iep-rule::after { content: ''; height: 1px; flex: 1; background: linear-gradient(to right, transparent, transparent); }
      .banner-accent-line { height: 3px; background: linear-gradient(90deg, #0f1f3d 0%, #c9820a 50%, #0f1f3d 100%); }
      
      @media (max-width: 860px) {
         .banner-inner { flex-direction: column; align-items: flex-start; padding: 40px 32px; }
         .banner-cta-card { width: 100%; text-align: left; }
         .cta-btn { text-align: center; }
         .star-bg { display: none; }
      }
      @media (max-width: 520px) {
         .banner-inner { padding: 32px 20px; }
         .trust-row { flex-direction: column; align-items: flex-start; gap: 10px; }
         .banner-cta-card { padding: 24px 20px; }
      }
</style>
"""

# HTML for English Pages
BANNER_EN = """
<!-- ======================================================================
     PREMIUM BANNER INJECTION
     ====================================================================== -->
<section id="iep-banner">
   <div class="banner-accent-line"></div>
   <div class="star-bg" aria-hidden="true">★</div>
   <div class="banner-inner">
      <div class="banner-text">
         <div class="banner-eyebrow" style="margin-bottom: 12px;">
            <span class="dot"></span>
            ⚠️ Expert Parent Tool
         </div>
         <h2 class="banner-headline">
            Think your child's<br>
            IEP rights are being<br>
            <em>ignored?</em>
         </h2>
         <p class="banner-sub" style="margin-bottom: 16px; font-size: 17px; color: #fff;">
            If your child isn’t getting the services, support, or evaluations they need…<br>
            <strong style="color: #f0a52a;">👉 You may be dealing with a legal violation—not just a school issue.</strong>
         </p>
         
         <p style="color: rgba(255,255,255,.6); font-size: 14px; margin-bottom: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">In under 3 minutes, we’ll show you:</p>
         <ul class="banner-feature-list">
            <li><span class="check">✓</span> Whether your child’s rights may be violated</li>
            <li><span class="check">✓</span> What the school is required to do (under law)</li>
            <li><span class="check">✓</span> What mistakes or red flags to watch for</li>
            <li><span class="check">✓</span> Exactly what steps you should take next</li>
         </ul>

         <div class="trust-row">
            <div class="trust-item"><span class="check">✓</span>Takes < 3 mins</div>
            <div class="trust-item"><span class="check">✓</span>No account required</div>
            <div class="trust-item"><span class="check">✓</span>100% private</div>
            <div class="trust-item"><span class="check">✓</span>Texas SPED specific</div>
         </div>
      </div>
      <div class="banner-cta-card">
         <p class="cta-card-label">📘 What You'll Receive</p>
         <p class="cta-card-desc">
            You’ll unlock a custom report built around your child’s situation, including:
         </p>
         <ul class="cta-feature-list">
            <li><span class="check">✓</span> A clear explanation of what’s happening</li>
            <li><span class="check">✓</span> The specific law or rule that applies</li>
            <li><span class="check">✓</span> A step-by-step action plan</li>
            <li><span class="check">✓</span> A copy/paste script to contact the school</li>
            <li><span class="check">✓</span> A checklist of documents to request</li>
         </ul>
         <a class="cta-btn" href="/backend/frontend/dashboard.html" target="_blank" rel="noopener">
            Analyze My Situation
            <span class="cta-btn-arrow">→</span>
         </a>
         <p class="cta-add-on">
            "Most parents who use this discover at least one issue they didn’t know was a violation."
         </p>
         <p class="cta-fine-print">
            ⚖️ Not Legal Advice — But Built on Real Texas Special Education Law
         </p>
      </div>
   </div>
</section>
<!-- ====================================================================== -->
"""

# HTML for Spanish Pages (Translated automatically for you)
BANNER_ES = """
<!-- ======================================================================
     PREMIUM BANNER INJECTION (ESPAÑOL)
     ====================================================================== -->
<section id="iep-banner">
   <div class="banner-accent-line"></div>
   <div class="star-bg" aria-hidden="true">★</div>
   <div class="banner-inner">
      <div class="banner-text">
         <div class="banner-eyebrow" style="margin-bottom: 12px;">
            <span class="dot"></span>
            ⚠️ Herramienta para Padres
         </div>
         <h2 class="banner-headline">
            ¿Cree que ignoran<br>
            los derechos del IEP<br>
            <em>de su hijo?</em>
         </h2>
         <p class="banner-sub" style="margin-bottom: 16px; font-size: 17px; color: #fff;">
            Si su hijo no recibe los servicios, el apoyo o las evaluaciones que necesita...<br>
            <strong style="color: #f0a52a;">👉 Podría tratarse de una violación legal, no solo un problema escolar.</strong>
         </p>
         
         <p style="color: rgba(255,255,255,.6); font-size: 14px; margin-bottom: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">En menos de 3 minutos, le mostraremos:</p>
         <ul class="banner-feature-list">
            <li><span class="check">✓</span> Si los derechos de su hijo podrían estar siendo violados</li>
            <li><span class="check">✓</span> Lo que la escuela debe hacer (por ley)</li>
            <li><span class="check">✓</span> Qué errores o señales de alerta buscar</li>
            <li><span class="check">✓</span> Exactamente qué pasos debe seguir a continuación</li>
         </ul>

         <div class="trust-row">
            <div class="trust-item"><span class="check">✓</span>Toma < 3 mins</div>
            <div class="trust-item"><span class="check">✓</span>Sin crear cuenta</div>
            <div class="trust-item"><span class="check">✓</span>100% privado</div>
            <div class="trust-item"><span class="check">✓</span>Específico de Texas</div>
         </div>
      </div>
      <div class="banner-cta-card">
         <p class="cta-card-label">📘 Lo que recibirá</p>
         <p class="cta-card-desc">
            Obtendrá un reporte personalizado basado en la situación de su hijo, que incluye:
         </p>
         <ul class="cta-feature-list">
            <li><span class="check">✓</span> Una explicación clara de lo que está sucediendo</li>
            <li><span class="check">✓</span> La ley o regla específica que aplica</li>
            <li><span class="check">✓</span> Un plan de acción paso a paso</li>
            <li><span class="check">✓</span> Un guion para contactar a la escuela</li>
            <li><span class="check">✓</span> Una lista de documentos para solicitar</li>
         </ul>
         <a class="cta-btn" href="/backend/frontend/dashboard.html" target="_blank" rel="noopener">
            Analizar mi situación
            <span class="cta-btn-arrow">→</span>
         </a>
         <p class="cta-add-on">
            "La mayoría de los padres descubren al menos un problema que no sabían que era una violación."
         </p>
         <p class="cta-fine-print">
            ⚖️ No es asesoría legal, pero se basa en la ley de educación especial de Texas
         </p>
      </div>
   </div>
</section>
<!-- ====================================================================== -->
"""

def process_files():
    files_updated = 0
    files_skipped = 0

    for root, dirs, files in os.walk(DIRECTORY):
        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if the banner is already in this file to prevent duplicates
                    if 'id="iep-banner"' in content:
                        files_skipped += 1
                        continue

                    # Check if we can find our target injection point
                    if '<div class="layout-grid">' not in content:
                        print(f"Skipping {filepath} (No layout-grid found)")
                        files_skipped += 1
                        continue

                    # Determine Language based on folder path
                    if '\\es\\' in filepath or '/es/' in filepath:
                        banner_to_use = BANNER_ES
                    else:
                        banner_to_use = BANNER_EN

                    # Inject CSS before closing </head>
                    if '</head>' in content:
                        content = content.replace('</head>', CSS_TO_INJECT + '\n</head>', 1)
                    
                    # Inject HTML Banner directly before the layout grid
                    content = content.replace('<div class="layout-grid">', banner_to_use + '\n<div class="layout-grid">', 1)

                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"Updated: {filepath}")
                    files_updated += 1
                    
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    print(f"\nDeployment Complete!")
    print(f"Successfully updated {files_updated} files.")
    print(f"Skipped {files_skipped} files (either already updated or incompatible layout).")

if __name__ == "__main__":
    process_files()