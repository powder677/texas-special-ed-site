import os
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# ======================================================================
# CONFIGURATION
# ======================================================================
# TODO: Replace with your actual Google Cloud Project ID
PROJECT_ID = "ard-intake-bot" 
LOCATION = "us-central1" # Or your preferred Vertex AI region
OUTPUT_DIRECTORY = "tefa_markdown_pages"
# ======================================================================
# PROMPT DICTIONARY
# ======================================================================
# Extracted from the ESA/TEFA Content Domination Framework

# Define your format instructions BEFORE the dictionary
en_format_instruction = "\n\nFormat the output in clean Markdown with clear H2 and H3 headings, bullet points, and an introduction/conclusion suitable for an SEO-optimized blog post."
es_format_instruction = "\n\nEscribe el resultado en formato Markdown limpio, usando un tono de 'Éxito Escolar' y 'familismo' (enfocado en recursos para la familia y ayuda para el hijo, sin etiquetas pesadas de discapacidad). Usa encabezados H2 y H3 claros adecuados para un blog optimizado para SEO."

RESEARCH_PROMPTS = {
    # ---------------- ENGLISH POSTS ---------------- #
  # ---------------- URGENCY & ADVOCACY POSTS (NEW) ---------------- #
    "EN-11": "Write an urgent, time-sensitive blog post with the exact headline: 'Missed the TEFA Deadline? Here's What Families Need to Know'. Frame the post around the real-time panic families are feeling after 200,000 applications were submitted for the original March 17 deadline. Reveal the critical, breaking news: The deadline has been officially extended to March 31, 2026. Explain exactly what parents must do right now to take advantage of this narrow extension, how to fast-track their application if they are missing documents, and why acting today is critical. The tone should be highly urgent, reassuring, and strictly action-oriented." + en_format_instruction,

    "EN-12": "Write a hard-hitting, advocacy-focused blog post exposing the biggest 'gotcha' of the Texas TEFA program. Focus on this critical detail: While an IEP is strictly required to trigger the $30,000 disability funding tier, private schools accepting TEFA funds are NOT legally required to provide the services listed in that IEP. Explain clearly that parents are effectively trading their federal IDEA rights and guaranteed services for this funding. Position the author/site as the only advocate telling families the full truth, and explain how parents must independently vet private schools to ensure their child's needs will be met without the protection of IDEA. The tone should be authoritative, protective, and slightly warning." + en_format_instruction,

    "ES-11": "Escribe un artículo de blog urgente y empoderador dirigido específicamente a familias hispanas en distritos como Socorro ISD y Aldine ISD sobre el orden de prioridad oficial de la lotería TEFA. Revela esta información crucial y confirmada: Las solicitudes se priorizan primero para estudiantes con discapacidades con ingresos familiares de hasta el 500% del Nivel Federal de Pobreza (FPL), luego el 200% del FPL, luego el 201-500% del FPL. Explica claramente a las familias latinas de bajos y medianos ingresos que están literalmente de primeros en la fila para recibir los $30,000, pero que la mayoría no lo sabe. Enfatiza que esta es una oportunidad histórica diseñada para ellos y dales los pasos exactos para asegurar su lugar en la parte superior de la lista." + es_format_instruction, 
}

def initialize_vertex():
    """Initializes the Vertex AI client and returns the model."""
    print(f"Initializing Vertex AI in project '{PROJECT_ID}'...")
    vertexai.init(project="ard-intake-bot", location="us-central1")
    # Gemini 1.5 Pro is recommended for complex reasoning and long-context research
    return GenerativeModel("gemini-2.5-flash")

def generate_markdown_pages(model):
    """Loops through the prompts, calls Vertex AI, and saves the Markdown files."""
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

    # Set temperature low (e.g., 0.2 - 0.3) to prioritize factual research over creative hallucination
    generation_config = GenerationConfig(
        temperature=0.2, 
    )

    for post_id, prompt in RESEARCH_PROMPTS.items():
        print(f"\n[+] Generating content for {post_id}...")
        try:
            # Call the model
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )

            # Create the file path
            filepath = os.path.join(OUTPUT_DIRECTORY, f"{post_id}.md")
            
            # Write to file
            with open(filepath, "w", encoding="utf-8") as f:
                # Optional: Add Markdown frontmatter for CMS importing (like WordPress or Hugo)
                f.write(f"---\nslug: {post_id.lower()}\nstatus: draft\n---\n\n")
                f.write(response.text)

            print(f"    -> Successfully saved to {filepath}")
            
        except Exception as e:
            print(f"    -> [ERROR] Failed to generate {post_id}: {e}")

if __name__ == "__main__":
    try:
        gemini_model = initialize_vertex()
        generate_markdown_pages(gemini_model)
        print(f"\n✅ All tasks complete. Check the '{OUTPUT_DIRECTORY}' folder.")
    except Exception as e:
        print(f"\n❌ Initialization Error. Did you set your PROJECT_ID and run 'gcloud auth application-default login'?\nDetails: {e}")