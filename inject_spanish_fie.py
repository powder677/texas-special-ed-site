"""
inject_spanish_fie.py
---------------------
Uses the Claude API to generate a Spanish "Cómo solicitar una FIE" section
(600–800 words) and injects it into each district's FIE HTML page, just
before the closing </article> tag in the content column.

Covers all 120 districts. CTA links → /resources/iep-letter-spanish/

Usage:
    pip install anthropic
    set ANTHROPIC_API_KEY=sk-ant-...        (Windows)
    export ANTHROPIC_API_KEY=sk-ant-...     (Mac/Linux)
    python inject_spanish_fie.py

Reads:  districts/{slug}/what-is-an-fie-{slug}.html
Writes: same file in place (backs up original as .bak once)
"""

import os
import re
import time
import anthropic

SCRIPT_DIR      = os.path.dirname(os.path.abspath(__file__))
DISTRICTS_DIR   = os.path.join(SCRIPT_DIR, "districts")
SPANISH_BOT_URL = "/resources/iep-letter-spanish/"

# Where to inject — just before article closes
INJECT_BEFORE = "</article>\n<!-- END LEFT COLUMN -->"
INJECT_BEFORE_ALT = "</article>"   # fallback if whitespace differs

# ── All 120 districts from your site ─────────────────────────────────────────

DISTRICTS = [
    {"name": "Houston ISD",                      "region": "Houston"},
    {"name": "Dallas ISD",                        "region": "Dallas"},
    {"name": "Cypress-Fairbanks ISD",             "region": "Houston"},
    {"name": "Northside ISD",                     "region": "San Antonio"},
    {"name": "Katy ISD",                          "region": "Houston"},
    {"name": "Fort Bend ISD",                     "region": "Houston"},
    {"name": "IDEA Public Schools",               "region": "Statewide"},
    {"name": "Conroe ISD",                        "region": "Houston"},
    {"name": "Austin ISD",                        "region": "Austin"},
    {"name": "Fort Worth ISD",                    "region": "Fort Worth"},
    {"name": "Frisco ISD",                        "region": "DFW"},
    {"name": "Aldine ISD",                        "region": "Houston"},
    {"name": "North East ISD",                    "region": "San Antonio"},
    {"name": "Arlington ISD",                     "region": "DFW"},
    {"name": "Klein ISD",                         "region": "Houston"},
    {"name": "Garland ISD",                       "region": "DFW"},
    {"name": "El Paso ISD",                       "region": "El Paso"},
    {"name": "Lewisville ISD",                    "region": "DFW"},
    {"name": "Plano ISD",                         "region": "DFW"},
    {"name": "Pasadena ISD",                      "region": "Houston"},
    {"name": "Humble ISD",                        "region": "Houston"},
    {"name": "Socorro ISD",                       "region": "El Paso"},
    {"name": "Round Rock ISD",                    "region": "Austin"},
    {"name": "San Antonio ISD",                   "region": "San Antonio"},
    {"name": "Killeen ISD",                       "region": "Central Texas"},
    {"name": "Lamar CISD",                        "region": "Houston"},
    {"name": "Leander ISD",                       "region": "Austin"},
    {"name": "United ISD",                        "region": "Laredo"},
    {"name": "Clear Creek ISD",                   "region": "Houston"},
    {"name": "Harmony Public Schools",            "region": "Statewide"},
    {"name": "Mesquite ISD",                      "region": "DFW"},
    {"name": "Richardson ISD",                    "region": "DFW"},
    {"name": "Alief ISD",                         "region": "Houston"},
    {"name": "Mansfield ISD",                     "region": "Fort Worth"},
    {"name": "Ysleta ISD",                        "region": "El Paso"},
    {"name": "Denton ISD",                        "region": "DFW"},
    {"name": "Ector County ISD",                  "region": "West Texas"},
    {"name": "Spring ISD",                        "region": "Houston"},
    {"name": "Spring Branch ISD",                 "region": "Houston"},
    {"name": "Corpus Christi ISD",                "region": "Coastal Bend"},
    {"name": "Keller ISD",                        "region": "Fort Worth"},
    {"name": "Irving ISD",                        "region": "DFW"},
    {"name": "Prosper ISD",                       "region": "DFW"},
    {"name": "Pharr-San Juan-Alamo ISD",          "region": "Rio Grande Valley"},
    {"name": "Alvin ISD",                         "region": "Houston"},
    {"name": "Amarillo ISD",                      "region": "Panhandle"},
    {"name": "Northwest ISD",                     "region": "Fort Worth"},
    {"name": "Comal ISD",                         "region": "San Antonio"},
    {"name": "Edinburg CISD",                     "region": "Rio Grande Valley"},
    {"name": "Midland ISD",                       "region": "West Texas"},
    {"name": "Judson ISD",                        "region": "San Antonio"},
    {"name": "Pflugerville ISD",                  "region": "Austin"},
    {"name": "Carrollton-Farmers Branch ISD",     "region": "DFW"},
    {"name": "Lubbock ISD",                       "region": "South Plains"},
    {"name": "Hays CISD",                         "region": "Austin"},
    {"name": "La Joya ISD",                       "region": "Rio Grande Valley"},
    {"name": "Eagle Mountain-Saginaw ISD",        "region": "Fort Worth"},
    {"name": "Goose Creek CISD",                  "region": "Houston"},
    {"name": "McKinney ISD",                      "region": "DFW"},
    {"name": "Tomball ISD",                       "region": "Houston"},
    {"name": "Birdville ISD",                     "region": "Fort Worth"},
    {"name": "Allen ISD",                         "region": "DFW"},
    {"name": "Hurst-Euless-Bedford ISD",          "region": "Fort Worth"},
    {"name": "Laredo ISD",                        "region": "Laredo"},
    {"name": "McAllen ISD",                       "region": "Rio Grande Valley"},
    {"name": "Wylie ISD",                         "region": "DFW"},
    {"name": "New Caney ISD",                     "region": "Houston"},
    {"name": "Rockwall ISD",                      "region": "DFW"},
    {"name": "Harlingen CISD",                    "region": "Rio Grande Valley"},
    {"name": "Crowley ISD",                       "region": "Fort Worth"},
    {"name": "Forney ISD",                        "region": "DFW"},
    {"name": "Weslaco ISD",                       "region": "Rio Grande Valley"},
    {"name": "Bryan ISD",                         "region": "Central Texas"},
    {"name": "Schertz-Cibolo-Universal City ISD", "region": "San Antonio"},
    {"name": "Magnolia ISD",                      "region": "Houston"},
    {"name": "Belton ISD",                        "region": "Central Texas"},
    {"name": "Abilene ISD",                       "region": "West Texas"},
    {"name": "College Station ISD",               "region": "Central Texas"},
    {"name": "Mission CISD",                      "region": "Rio Grande Valley"},
    {"name": "Donna ISD",                         "region": "Rio Grande Valley"},
    {"name": "Coppell ISD",                       "region": "DFW"},
    {"name": "Grapevine-Colleyville ISD",         "region": "DFW"},
    {"name": "San Angelo ISD",                    "region": "West Texas"},
    {"name": "Bastrop ISD",                       "region": "Austin"},
    {"name": "Wichita Falls ISD",                 "region": "North Texas"},
    {"name": "Dickinson ISD",                     "region": "Houston"},
    {"name": "Burleson ISD",                      "region": "Fort Worth"},
    {"name": "Lake Travis ISD",                   "region": "Austin"},
    {"name": "East Central ISD",                  "region": "San Antonio"},
    {"name": "Del Valle ISD",                     "region": "Austin"},
    {"name": "Clint ISD",                         "region": "El Paso"},
    {"name": "Sherman ISD",                       "region": "North Texas"},
    {"name": "Georgetown ISD",                    "region": "Austin"},
    {"name": "Montgomery ISD",                    "region": "Houston"},
    {"name": "Royse City ISD",                    "region": "DFW"},
    {"name": "Rio Grande City Grulla ISD",        "region": "Rio Grande Valley"},
    {"name": "San Benito CISD",                   "region": "Rio Grande Valley"},
    {"name": "Waller ISD",                        "region": "Houston"},
    {"name": "Little Elm ISD",                    "region": "DFW"},
    {"name": "Midway ISD",                        "region": "Central Texas"},
    {"name": "Temple ISD",                        "region": "Central Texas"},
    {"name": "San Marcos CISD",                   "region": "Austin"},
    {"name": "Longview ISD",                      "region": "East Texas"},
    {"name": "Eanes ISD",                         "region": "Austin"},
    {"name": "Texas City ISD",                    "region": "Houston"},
    {"name": "Seguin ISD",                        "region": "San Antonio"},
    {"name": "Texarkana ISD",                     "region": "East Texas"},
    {"name": "Copperas Cove ISD",                 "region": "Central Texas"},
    {"name": "Crosby ISD",                        "region": "Houston"},
    {"name": "Princeton ISD",                     "region": "DFW"},
    {"name": "Melissa ISD",                       "region": "DFW"},
    {"name": "Friendswood ISD",                   "region": "Houston"},
    {"name": "Channelview ISD",                   "region": "Houston"},
    {"name": "Victoria ISD",                      "region": "Coastal Bend"},
    {"name": "Waco ISD",                          "region": "Central Texas"},
    {"name": "Beaumont ISD",                      "region": "Southeast Texas"},
    {"name": "Tyler ISD",                         "region": "East Texas"},
    {"name": "Santa Fe ISD",                      "region": "Houston"},
    {"name": "Grand Prairie ISD",                 "region": "DFW"},
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def to_slug(name):
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = slug.strip()
    slug = re.sub(r"\s+", "-", slug)
    return slug


def build_prompt(district_name, region):
    return f"""Eres redactor para texasspecialed.com, un sitio de recursos para padres de Texas sobre educación especial.

Escribe una sección en español para la página de {district_name} con este título exacto como etiqueta <h2>:
"Cómo solicitar una evaluación FIE en {district_name}"

REQUISITOS DE CONTENIDO (obligatorios):
- Mínimo 600 palabras, máximo 800 palabras
- Lenguaje cálido y accesible para padres hispanos en la región {region} de Texas
- Menciona {district_name} por nombre al menos 3 veces a lo largo del texto
- Explica qué es una FIE (Evaluación Individual Completa) en términos sencillos
- Cita la ley: IDEA y Capítulo 29 del Código de Educación de Texas
- Incluye los plazos legales: 15 días escolares para que el distrito responda, 45 días escolares para completar la evaluación
- Explica la diferencia entre FIE y FIIE (Evaluación Individual e Inicial Completa)
- Incluye una subsección sobre los derechos del padre si el distrito se niega a evaluar
- El único enlace en todo el contenido debe ser el CTA final: {SPANISH_BOT_URL}

ESTRUCTURA Y CLASES HTML (usa solo estas):
  <h2>  título principal de la sección
  <h3>  subtítulos internos (2 o 3 máximo)
  <p>   párrafos
  <div class="pull-quote">  una sola cita destacada
  <div class="warning-box"><p>...</p></div>  una advertencia legal
  <div class="action-steps">
    <h3>Pasos para solicitar la evaluación</h3>
    <ol><li><strong>Nombre del paso:</strong> descripción</li></ol>
  </div>

BLOQUE CTA FINAL — incluye este bloque EXACTO al final, sin cambiarlo:
<div class="inline-cta" style="background:#fdfaf5;border:1px solid #d6cbbf;border-left:4px solid #b8963a;border-radius:6px;padding:24px;margin:2.5rem 0;display:flex;gap:16px;align-items:flex-start;">
<div class="cta-icon">📝</div>
<div>
<h3 style="margin:0 0 8px;font-family:'Lora',serif;font-size:1.3rem;color:#0a2342;border:none;padding:0;">¿Lista para enviar tu solicitud a {district_name}?</h3>
<p style="margin:0 0 16px;font-size:16px;color:#475569;">Usa nuestro generador gratuito en español para redactar una carta con validez legal en minutos. El sistema cita el Capítulo 29 del Código de Educación de Texas y obliga a {district_name} a responder en 15 días escolares.</p>
<a href="{SPANISH_BOT_URL}" style="background:#b8963a;color:#fff;padding:12px 24px;text-decoration:none;border-radius:4px;font-weight:600;font-size:15px;display:inline-block;">Generar mi carta en español →</a>
</div>
</div>

REGLAS FINALES:
- Devuelve SOLO el HTML de la sección
- Sin <!DOCTYPE>, <html>, <head>, <body>, ni bloques de código markdown
- No inventes clases ni estilos nuevos
- El único href permitido es {SPANISH_BOT_URL}"""


# ── Call Claude API ───────────────────────────────────────────────────────────

def generate_spanish_section(client, district_name, region):
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1800,
        messages=[{"role": "user", "content": build_prompt(district_name, region)}],
    )
    raw = message.content[0].text.strip()
    raw = re.sub(r"^```(?:html)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    return raw


# ── Inject into existing HTML file ───────────────────────────────────────────

def inject_into_file(filepath, spanish_html):
    with open(filepath, "r", encoding="utf-8") as f:
        original = f.read()

    # Already done?
    if "Cómo solicitar una evaluación FIE" in original:
        return False, "already injected"

    # Find the right injection point
    if INJECT_BEFORE in original:
        marker = INJECT_BEFORE
    elif INJECT_BEFORE_ALT in original:
        marker = INJECT_BEFORE_ALT
    else:
        return False, "injection marker </article> not found in file"

    block = (
        "\n<!-- SECCION EN ESPAÑOL ──────────────────────────────── -->\n"
        "<div class=\"section-divider\">· · ·</div>\n"
        "<section id=\"seccion-espanol\" lang=\"es\">\n"
        f"{spanish_html}\n"
        "</section>\n"
        "<!-- FIN SECCION EN ESPAÑOL ──────────────────────────── -->\n\n"
    )

    updated = original.replace(marker, block + marker, 1)

    # Write backup once (never overwrite an existing .bak)
    bak = filepath + ".bak"
    if not os.path.exists(bak):
        with open(bak, "w", encoding="utf-8") as f:
            f.write(original)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(updated)

    return True, "ok"


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "\n❌ ANTHROPIC_API_KEY is not set.\n"
            "   Windows : set ANTHROPIC_API_KEY=sk-ant-...\n"
            "   Mac/Linux: export ANTHROPIC_API_KEY=sk-ant-...\n"
        )

    client   = anthropic.Anthropic(api_key=api_key)
    total    = len(DISTRICTS)
    injected = 0
    skipped  = 0
    missing  = 0
    errors   = []

    print(f"Processing {total} district FIE pages...\n")

    for idx, district in enumerate(DISTRICTS, start=1):
        name   = district["name"]
        region = district["region"]
        slug   = to_slug(name)
        filepath = os.path.join(DISTRICTS_DIR, slug, f"what-is-an-fie-{slug}.html")

        # ── File doesn't exist yet ────────────────────────────────────────────
        if not os.path.exists(filepath):
            missing += 1
            print(f"[{idx:03d}/{total}] ⚠  NOT FOUND  districts/{slug}/what-is-an-fie-{slug}.html")
            continue

        print(f"[{idx:03d}/{total}] {name} ...", end=" ", flush=True)

        try:
            spanish_html        = generate_spanish_section(client, name, region)
            success, reason     = inject_into_file(filepath, spanish_html)

            if success:
                injected += 1
                print("✓")
            else:
                skipped += 1
                print(f"– skipped ({reason})")

        except anthropic.RateLimitError:
            print("⚠  rate limited — waiting 60s ...")
            time.sleep(60)
            try:
                spanish_html    = generate_spanish_section(client, name, region)
                success, reason = inject_into_file(filepath, spanish_html)
                injected += 1 if success else 0
                skipped  += 0 if success else 1
                print("✓ (after retry)" if success else f"– skipped ({reason})")
            except Exception as e:
                errors.append((name, str(e)))
                print(f"✗ ERROR: {e}")

        except Exception as e:
            errors.append((name, str(e)))
            print(f"✗ ERROR: {e}")

        if idx < total:
            time.sleep(1.5)

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅  Injected          : {injected}
  ⏭️   Skipped           : {skipped}  (already injected)
  ⚠️   FIE pages missing : {missing}  (run assemble + deploy first)
  ❌  Errors            : {len(errors)}
  🔗  Spanish CTA link  : {SPANISH_BOT_URL}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

    if missing:
        print(
            "ℹ️  Missing FIE pages: run assemble_fie_pages.py and deploy_fie_pages.py\n"
            "   for those districts first, then re-run this script.\n"
        )

    if errors:
        print("Error details:")
        for n, msg in errors:
            print(f"  {n}: {msg}")


if __name__ == "__main__":
    main()