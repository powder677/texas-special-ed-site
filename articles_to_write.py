import os
import anthropic

# Check for API key before running
if not os.environ.get("ANTHROPIC_API_KEY"):
    raise ValueError("ANTHROPIC_API_KEY environment variable not set. Please set it before running.")

def generate_spanish_seo_article(title, keyword, slug):
    """
    Generates a 1200+ word SEO article in Spanish using Claude.
    """
    client = anthropic.Anthropic()
    
    system_prompt = """
    You are an expert bilingual Special Education Advocate and SEO content writer. 
    Your goal is to write a highly empathetic, informative, and SEO-optimized Spanish article for parents in Texas.
    
    STRICT REQUIREMENTS:
    - Minimum length: 1200 words.
    - Tone: Empathetic, supportive, authoritative, and fact-based regarding Texas education law.
    - Formatting: Use scannable H2 and H3 tags, bullet points, and short paragraphs.
    
    FUNNEL STRUCTURE:
    1. Validate the Parent's Problem (e.g., emotional trigger, fear of child falling behind).
    2. Explain the Disability Possibility (e.g., Dyslexia, ADHD, Learning Disabilities).
    3. Explain FIE Evaluation Rights (Mention IDEA and Child Find laws).
    4. Call to Action: Aggressively but naturally push the user to generate an official FIE request letter. 
       Always include this exact Markdown link in the CTA: [Carta para Solicitar Evaluación FIE](/es/carta-evaluacion-educacion-especial-texas).
       
    Include a robust FAQ section at the end with questions formatted as H3s to capture Google featured snippets.
    """
    
    user_prompt = f"""
    Please write the article now based on these parameters:
    - Page Title: {title}
    - Primary Keyword: {keyword}
    - URL Slug: {slug}
    
    Make sure to address the fact that schools cannot force parents to wait for RTI (Response to Intervention) before evaluating.
    """
    
    try:
        print(f"Generating article for: {title}...")
        
        # Fixed: Using the correct Claude 4 model that worked for you earlier
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        article_content = message.content[0].text
        
        # Save files to the correct directory structure
        filename = os.path.join("blog", "es", f"{slug}.md")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(article_content)
            
        print(f"✅ Successfully generated and saved to {filename}\n")
        return article_content

    except Exception as e:
        print(f"❌ Error generating article: {e}")
        return None

if __name__ == "__main__":
    # The remaining 6 high-intent Spanish SEO articles
    articles_to_write = [
        # --- CORE TRAFFIC PAGES ---
        {
            "title": "¿Qué es una Evaluación FIE en Texas?",
            "keyword": "que es fie escuela",
            "slug": "que-es-fie-texas"
        },
        {
            "title": "Cómo Solicitar una Evaluación de Educación Especial para su Hijo",
            "keyword": "como pedir evaluacion escolar",
            "slug": "como-solicitar-evaluacion-educacion-especial"
        },
        {
            "title": "Cuánto Tiempo Toma una Evaluación FIE en Texas",
            "keyword": "tiempo evaluacion fie texas",
            "slug": "tiempo-evaluacion-fie-texas"
        },
        {
            "title": "¿La Escuela Negó la Evaluación para su Hijo? Qué Hacer Ahora",
            "keyword": "escuela nego evaluacion",
            "slug": "escuela-nego-evaluacion"
        },
        # --- REMAINING PROBLEM-BASED PAGES ---
        {
            "title": "¿El Maestro Dice que su Hijo “No Se Esfuerza”? Podría Ser una Discapacidad de Aprendizaje",
            "keyword": "maestro dice mi hijo no se esfuerza",
            "slug": "maestro-dice-mi-hijo-no-se-esfuerza"
        },
        {
            "title": "¿Su Hijo No Se Puede Concentrar en Clase? Podría Tener TDAH y Necesitar un IEP",
            "keyword": "mi hijo no se concentra en la escuela",
            "slug": "mi-hijo-no-se-concentra-en-clase"
        }
    ]

    for article in articles_to_write:
        generate_spanish_seo_article(
            title=article["title"], 
            keyword=article["keyword"], 
            slug=article["slug"]
        )