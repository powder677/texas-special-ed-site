import os
from bs4 import BeautifulSoup

# Archivos que NO queremos modificar (sin importar en qué carpeta estén)
SKIP_FILES = ['index.html', 'template.html']

def extract_core_content(soup):
    """
    Extrae solo el contenido principal del artículo de un archivo HTML,
    ignorando barras de navegación, encabezados y pies de página antiguos.
    """
    # 1er Intento: Si el archivo ya tiene el contenedor de la plantilla
    article = soup.find('article', class_='content-column')
    if article:
        return article.decode_contents()
    
    # 2do Intento: Si es una página HTML completa, limpiar y extraer el body
    if soup.body:
        # Eliminar elementos de la plantilla vieja que no queremos duplicar
        for tag in soup.body.find_all(['header', 'footer', 'nav']):
            tag.decompose()
        
        # Eliminar contenedores principales si existen, para no anidar <main> dentro de <article>
        main_tag = soup.body.find('main')
        if main_tag:
            return main_tag.decode_contents()
            
        return soup.body.decode_contents()
    
    # 3er Intento: Si es un fragmento de código (snippet sin <body>)
    return soup.decode_contents()

def update_files():
    # 1. Cargar la plantilla base desde el directorio principal
    try:
        with open('template.html', 'r', encoding='utf-8') as f:
            template_html = f.read()
    except FileNotFoundError:
        print("❌ Error: No se encontró 'template.html' en esta carpeta.")
        return

    # 2. Buscar todos los archivos HTML en todas las subcarpetas (carpetas de distritos)
    html_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.html') and file not in SKIP_FILES:
                # Guardamos la ruta completa (ej. ALDINE ISD/como-solicitar.html)
                html_files.append(os.path.join(root, file))

    if not html_files:
        print("No se encontraron archivos HTML para actualizar en las carpetas.")
        return

    print(f"Iniciando actualización de {len(html_files)} archivos en las carpetas...\n")

    for filepath in html_files:
        try:
            # 3. Leer el contenido del archivo a actualizar usando su ruta completa
            with open(filepath, 'r', encoding='utf-8') as f:
                target_soup = BeautifulSoup(f.read(), 'html.parser')

            # Extraer solo el contenido útil
            core_content = extract_core_content(target_soup)

            # 4. Crear una copia fresca de la plantilla
            soup = BeautifulSoup(template_html, 'html.parser')
            article_container = soup.find('article', class_='content-column')

            if not article_container:
                print("❌ Error en la plantilla: No se encontró <article class='content-column'>")
                return

            # 5. Vaciar la plantilla e inyectar el nuevo contenido
            article_container.clear()
            
            # Insertar el contenido parseado como HTML real, no como texto plano
            content_soup = BeautifulSoup(core_content, 'html.parser')
            article_container.append(content_soup)

            # 6. Actualizar la etiqueta <title> basándose en el <h1> del artículo
            h1_tag = content_soup.find('h1')
            if h1_tag:
                title_tag = soup.find('title')
                if title_tag:
                    title_text = h1_tag.get_text(strip=True).replace('  ', ' ')
                    title_tag.string = f"{title_text} | Texas Special Ed"

            # 7. Guardar el archivo modificado de vuelta en su ubicación original
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))

            print(f"  ✅ Actualizado con éxito: {filepath}")

        except Exception as e:
            print(f"  ❌ Error al procesar {filepath}: {e}")

    print("\n🎉 ¡Proceso completado!")

if __name__ == '__main__':
    update_files()