import os
import shutil

# --- CONFIGURACIÓN ---
# ¡IMPORTANTE! Cambia estas dos rutas por las tuyas.

# Ruta a la carpeta de tu proyecto original (la que tiene muchas subcarpetas).
# ruta_origen = "/home/dseveria/hack/titan-on-ocp-poc"
ruta_origen = "/home/dseveria/hack/ocp-gitops-architecture"


# Ruta a la carpeta vacía que creaste para guardar todos los archivos.
# ruta_destino = "/home/dseveria/hack/titan-on-ocp-poc-flat"
ruta_destino = "/home/dseveria/hack/ocp-gitops-architecture-flat"

# Extensiones de archivo permitidas
EXTENSIONES_PERMITIDAS = {
    'pdf', 'txt', 'md', '3g2', '3gp', 'aac', 'aif', 'aifc', 'aiff', 'amr', 
    'au', 'avi', 'cda', 'm4a', 'mid', 'mp3', 'mp4', 'mpeg', 'ogg', 'opus', 
    'ra', 'ram', 'snd', 'wav', 'wma'
}

# Límites de control
MAX_FILE_SIZE_MB = 200  # Tamaño máximo por archivo en MB
MAX_WORDS_PER_FILE = 500000  # Máximo de palabras por archivo
MAX_FILES_PER_FOLDER = 300  # Máximo de archivos por carpeta
MAX_IMAGENES_PER_FOLDER = 10  # Máximo de imágenes por carpeta

# Extensiones de imágenes que se copiarán a carpeta separada
EXTENSIONES_IMAGENES = {
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'ico', 'tiff', 'webp', 'tga', 'psd', 'ai', 'eps', 'xcf', 'graphml'
}
# ---------------------


def es_extension_permitida(extension):
    """
    Verifica si la extensión del archivo está en la lista de extensiones permitidas.
    """
    return extension.lower().lstrip('.') in EXTENSIONES_PERMITIDAS


def es_imagen(extension):
    """
    Verifica si la extensión del archivo corresponde a una imagen.
    """
    return extension.lower().lstrip('.') in EXTENSIONES_IMAGENES


def es_archivo_excluido(extension):
    """
    Verifica si la extensión del archivo debe ser excluida del procesamiento.
    """
    extensiones_excluidas = {'ttf', 'otf', 'woff', 'woff2', 'eot'}  # Fuentes
    return extension.lower().lstrip('.') in extensiones_excluidas


def limpiar_shebang_shell(ruta_archivo):
    """
    Lee un archivo shell script y elimina la línea del shebang (#!/bin/bash, #!/bin/sh, etc.)
    Retorna el contenido limpio o None si hay error.
    """
    try:
        # Intentar leer con diferentes encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(ruta_archivo, 'r', encoding=encoding) as archivo:
                    lineas = archivo.readlines()
                
                # Filtrar líneas que empiecen con #!/ (shebang)
                lineas_limpias = []
                for linea in lineas:
                    linea_stripped = linea.strip()
                    # Eliminar cualquier línea que empiece con #!/
                    if not linea_stripped.startswith('#!/'):
                        lineas_limpias.append(linea)
                
                return ''.join(lineas_limpias)
                
            except UnicodeDecodeError:
                continue
        
        # Si no se puede leer como texto, retornar None
        return None
        
    except Exception as e:
        print(f"  !! Error al limpiar shebang de {ruta_archivo}: {e}")
        return None




def verificar_tamaño_archivo(ruta_archivo):
    """
    Verifica si el archivo no supera el tamaño máximo permitido.
    Retorna True si el archivo es válido, False si es demasiado grande.
    """
    try:
        tamaño_bytes = os.path.getsize(ruta_archivo)
        tamaño_mb = tamaño_bytes / (1024 * 1024)  # Convertir a MB
        
        if tamaño_mb > MAX_FILE_SIZE_MB:
            print(f"  !! Archivo demasiado grande ({tamaño_mb:.2f} MB > {MAX_FILE_SIZE_MB} MB): {ruta_archivo}")
            return False
        return True
    except Exception as e:
        print(f"  !! Error al verificar tamaño de {ruta_archivo}: {e}")
        return False


def contar_palabras_archivo(ruta_archivo):
    """
    Cuenta las palabras en un archivo de texto.
    Retorna el número de palabras o -1 si hay error.
    """
    try:
        # Intentar leer como texto con diferentes encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(ruta_archivo, 'r', encoding=encoding) as archivo:
                    contenido = archivo.read()
                    # Contar palabras separadas por espacios, saltos de línea, etc.
                    palabras = len(contenido.split())
                    return palabras
            except UnicodeDecodeError:
                continue
        
        # Si no se puede leer como texto, asumir que es binario y contar bytes
        with open(ruta_archivo, 'rb') as archivo:
            contenido = archivo.read()
            # Para archivos binarios, estimar palabras basándose en el tamaño
            # Asumiendo ~5 caracteres por palabra en promedio
            palabras_estimadas = len(contenido) // 5
            return palabras_estimadas
            
    except Exception as e:
        print(f"  !! Error al contar palabras en {ruta_archivo}: {e}")
        return -1


def verificar_palabras_archivo(ruta_archivo):
    """
    Verifica si el archivo no supera el límite de palabras.
    Retorna True si el archivo es válido, False si tiene demasiadas palabras.
    """
    palabras = contar_palabras_archivo(ruta_archivo)
    
    if palabras == -1:  # Error al leer el archivo
        return False
    
    if palabras > MAX_WORDS_PER_FILE:
        print(f"  !! Archivo con demasiadas palabras ({palabras:,} > {MAX_WORDS_PER_FILE:,}): {ruta_archivo}")
        return False
    
    return True


def eliminar_archivos_vacios(directorio):
    """
    Elimina todos los archivos vacíos (0 bytes) del directorio especificado.
    """
    archivos_eliminados = 0
    
    print(f"\nBuscando archivos vacíos en: {directorio}")
    
    for dirpath, _, filenames in os.walk(directorio):
        for filename in filenames:
            ruta_archivo = os.path.join(dirpath, filename)
            
            try:
                # Verificar si el archivo está vacío
                if os.path.getsize(ruta_archivo) == 0:
                    print(f"  -> Eliminando archivo vacío: {ruta_archivo}")
                    os.remove(ruta_archivo)
                    archivos_eliminados += 1
            except Exception as e:
                print(f"  !! Error al procesar {ruta_archivo}: {e}")
    
    print(f"Total de archivos vacíos eliminados: {archivos_eliminados}")
    return archivos_eliminados


def convertir_extension_a_txt(filename):
    """
    Convierte la extensión de un archivo a una extensión válida similar al tipo original.
    Muestra el tipo original y la transformación aplicada.
    """
    nombre_base, extension = os.path.splitext(filename)
    extension_lower = extension.lower()
    
    # Si no tiene extensión, agregar .txt
    if not extension:
        nuevo_nombre = f"{nombre_base}.txt"
        print(f"  -> Agregando extensión: sin extensión → '.txt' (archivo: {filename})")
        return nuevo_nombre
    
    # Mapeo de extensiones a extensiones válidas más similares
    mapeo_extensiones = {
        # Scripts y código
        '.sh': '.md',           # Shell scripts → Markdown
        '.bash': '.md',         # Bash scripts → Markdown
        '.zsh': '.md',          # Zsh scripts → Markdown
        '.py': '.txt',          # Python → Texto
        '.js': '.txt',          # JavaScript → Texto
        '.ts': '.txt',          # TypeScript → Texto
        '.java': '.txt',        # Java → Texto
        '.cpp': '.txt',         # C++ → Texto
        '.c': '.txt',           # C → Texto
        '.h': '.txt',           # Header files → Texto
        '.php': '.txt',         # PHP → Texto
        '.rb': '.txt',          # Ruby → Texto
        '.go': '.txt',          # Go → Texto
        '.rs': '.txt',          # Rust → Texto
        '.swift': '.txt',       # Swift → Texto
        '.kt': '.txt',          # Kotlin → Texto
        '.scala': '.txt',       # Scala → Texto
        '.pl': '.txt',          # Perl → Texto
        '.lua': '.txt',         # Lua → Texto
        '.r': '.txt',           # R → Texto
        '.m': '.txt',           # MATLAB/Objective-C → Texto
        
        # Configuración y datos
        '.yaml': '.txt',        # YAML → Texto
        '.yml': '.txt',         # YAML → Texto
        '.json': '.txt',        # JSON → Texto
        '.xml': '.txt',         # XML → Texto
        '.ini': '.txt',         # INI → Texto
        '.cfg': '.txt',         # Config → Texto
        '.conf': '.txt',        # Config → Texto
        '.properties': '.txt',  # Properties → Texto
        '.env': '.txt',         # Environment → Texto
        '.toml': '.txt',        # TOML → Texto
        '.csv': '.txt',         # CSV → Texto
        '.tsv': '.txt',         # TSV → Texto
        
        # Documentación
        '.adoc': '.txt',        # AsciiDoc → Texto
        '.rst': '.txt',         # reStructuredText → Texto
        '.tex': '.txt',         # LaTeX → Texto
        '.org': '.txt',         # Org mode → Texto
        
        # Templates y otros
        '.template': '.txt',    # Template → Texto
        '.tpl': '.txt',         # Template → Texto
        '.mustache': '.txt',    # Mustache → Texto
        '.hbs': '.txt',         # Handlebars → Texto
        '.ejs': '.txt',         # EJS → Texto
        
        # Docker y contenedores
        '.dockerfile': '.txt',  # Dockerfile → Texto
        '.dockerignore': '.txt', # Docker ignore → Texto
        
        # Otros archivos de texto
        '.log': '.txt',         # Log files → Texto
        '.sql': '.txt',         # SQL → Texto
        '.diff': '.txt',        # Diff → Texto
        '.patch': '.txt',       # Patch → Texto
        '.gitignore': '.txt',   # Git ignore → Texto
        '.gitattributes': '.txt', # Git attributes → Texto
        
        # Las imágenes se manejan por separado, no se incluyen aquí
        
        # Diagramas y diseño
        '.excalidraw': '.txt',  # Excalidraw → Texto
        '.drawio': '.txt',      # Draw.io → Texto
        '.vsdx': '.txt',        # Visio → Texto
        '.dwg': '.txt',         # AutoCAD → Texto
        
        # Archivos comprimidos (convertir a texto descriptivo)
        '.zip': '.txt',         # ZIP → Texto
        '.tar': '.txt',         # TAR → Texto
        '.gz': '.txt',          # GZIP → Texto
        '.rar': '.txt',         # RAR → Texto
        '.7z': '.txt',          # 7-Zip → Texto
        
        # Binarios (convertir a texto descriptivo)
        '.exe': '.txt',         # Executable → Texto
        '.dll': '.txt',         # DLL → Texto
        '.so': '.txt',          # Shared Object → Texto
        '.dylib': '.txt',       # Dynamic Library → Texto
        '.bin': '.txt',         # Binary → Texto
    }
    
    # Si la extensión está permitida, no hacer nada
    if es_extension_permitida(extension):
        return filename
    
    # Buscar en el mapeo
    if extension_lower in mapeo_extensiones:
        nueva_extension = mapeo_extensiones[extension_lower]
        nuevo_nombre = f"{nombre_base}{nueva_extension}"
        print(f"  -> Conversión de extensión: '{extension}' → '{nueva_extension}' (archivo: {filename})")
        return nuevo_nombre
    
    # Si no está en el mapeo, usar .txt como fallback
    nuevo_nombre = f"{nombre_base}.txt"
    print(f"  -> Conversión de extensión: '{extension}' → '.txt' (fallback, archivo: {filename})")
    return nuevo_nombre


def aplanar_directorio(origen, destino):
    """
    Copia todos los archivos de un directorio de origen y sus subdirectorios
    a directorios de destino, manejando conflictos de nombres y controles de tamaño.
    """
    # 1. Asegurarse de que la carpeta de destino base existe.
    if not os.path.exists(destino):
        print(f"Creando directorio de destino: {destino}")
        os.makedirs(destino)

    print(f"Buscando archivos en: {origen}")
    print(f"Copiando archivos a: {destino}")
    print(f"Límites: {MAX_FILE_SIZE_MB} MB por archivo, {MAX_WORDS_PER_FILE:,} palabras por archivo, {MAX_FILES_PER_FOLDER} archivos por carpeta\n")

    # Contadores para control de múltiples carpetas
    archivos_copiados = 0
    imagenes_copiadas = 0
    carpeta_actual = 1
    carpeta_imagenes_actual = 1
    directorio_destino_actual = destino
    
    # Crear la primera carpeta si es necesario
    if not os.path.exists(directorio_destino_actual):
        print(f"Creando carpeta inicial: {directorio_destino_actual}")
        os.makedirs(directorio_destino_actual)
    
    # Crear primera carpeta para imágenes
    directorio_imagenes_actual = os.path.join(destino, f"imagenes_{carpeta_imagenes_actual}")
    if not os.path.exists(directorio_imagenes_actual):
        print(f"Creando carpeta para imágenes: {directorio_imagenes_actual}")
        os.makedirs(directorio_imagenes_actual)
    
    # 2. Recorrer cada carpeta, subcarpeta y archivo en el origen.
    for dirpath, _, filenames in os.walk(origen):
        # Ignorar el directorio .git por completo
        if ".git" in dirpath.split(os.sep):
            continue
            
        for filename in filenames:
            # Construir la ruta completa del archivo original
            ruta_archivo_original = os.path.join(dirpath, filename)
            
            # Obtener la extensión del archivo
            _, extension = os.path.splitext(filename)
            
            # 3. Verificar si el archivo debe ser excluido
            if es_archivo_excluido(extension):
                print(f"  -> Archivo excluido (extensión {extension}): {filename}")
                continue
            
            # 4. Verificar tamaño del archivo
            if not verificar_tamaño_archivo(ruta_archivo_original):
                continue
            
            # 4.5. Si no tiene extensión, verificar que tenga contenido antes de agregar .txt
            if not extension:
                try:
                    # Verificar si el archivo tiene contenido (no está vacío)
                    if os.path.getsize(ruta_archivo_original) == 0:
                        print(f"  -> Archivo sin extensión y vacío, omitiendo: {filename}")
                        continue
                except Exception as e:
                    print(f"  !! Error al verificar archivo sin extensión {ruta_archivo_original}: {e}")
                    continue
            
            # 5. Verificar si es una imagen
            if es_imagen(extension):
                # Crear nueva carpeta de imágenes si se alcanzó el límite
                if imagenes_copiadas > 0 and imagenes_copiadas % MAX_IMAGENES_PER_FOLDER == 0:
                    carpeta_imagenes_actual += 1
                    directorio_imagenes_actual = os.path.join(destino, f"imagenes_{carpeta_imagenes_actual}")
                    if not os.path.exists(directorio_imagenes_actual):
                        print(f"Creando nueva carpeta de imágenes: {directorio_imagenes_actual}")
                        os.makedirs(directorio_imagenes_actual)
                
                # Manejar imágenes por separado
                ruta_imagen_destino = os.path.join(directorio_imagenes_actual, filename)
                
                # Manejo de conflictos para imágenes
                contador = 1
                nombre_base, ext = os.path.splitext(filename)
                
                while os.path.exists(ruta_imagen_destino):
                    nuevo_nombre = f"{nombre_base}_{contador}{ext}"
                    ruta_imagen_destino = os.path.join(directorio_imagenes_actual, nuevo_nombre)
                    contador += 1
                
                try:
                    if ruta_imagen_destino != os.path.join(directorio_imagenes_actual, filename):
                        print(f"  -> Conflicto detectado para imagen '{filename}'. Renombrando a '{os.path.basename(ruta_imagen_destino)}'")
                    
                    shutil.copy2(ruta_archivo_original, ruta_imagen_destino)
                    imagenes_copiadas += 1
                    print(f"  -> Imagen copiada: {filename} (carpeta imagenes_{carpeta_imagenes_actual})")
                    
                except Exception as e:
                    print(f"  !! Error al copiar imagen {ruta_archivo_original}: {e}")
                
                continue
            
            # 6. Verificar número de palabras del archivo (solo para archivos no-imagen)
            if not verificar_palabras_archivo(ruta_archivo_original):
                continue
            
            # 7. Crear nueva carpeta si se alcanzó el límite de archivos
            if archivos_copiados > 0 and archivos_copiados % MAX_FILES_PER_FOLDER == 0:
                carpeta_actual += 1
                directorio_destino_actual = os.path.join(destino, f"carpeta_{carpeta_actual}")
                if not os.path.exists(directorio_destino_actual):
                    print(f"Creando nueva carpeta: {directorio_destino_actual}")
                    os.makedirs(directorio_destino_actual)
            
            # Convertir la extensión si no está permitida
            filename_convertido = convertir_extension_a_txt(filename)
            
            # Construir la ruta tentativa en el destino
            ruta_archivo_destino = os.path.join(directorio_destino_actual, filename_convertido)
            
            # Procesar contenido especial según el tipo de archivo
            contenido_limpio = None
            
            # Si es un archivo .sh convertido a .md, limpiar el shebang
            if filename_convertido.endswith('.md') and (filename.endswith('.sh') or filename.endswith('.bash')):
                contenido_limpio = limpiar_shebang_shell(ruta_archivo_original)
                if contenido_limpio is not None:
                    print(f"  -> Shebang eliminado de: {filename}")
            
           
            
            # 8. Manejo de conflictos: verificar si ya existe un archivo con ese nombre.
            contador = 1
            nombre_base, extension = os.path.splitext(filename_convertido)
            
            while os.path.exists(ruta_archivo_destino):
                # Si existe, crea un nuevo nombre con un sufijo numérico
                nuevo_nombre = f"{nombre_base}_{contador}{extension}"
                ruta_archivo_destino = os.path.join(directorio_destino_actual, nuevo_nombre)
                contador += 1

            # 9. Copiar el archivo (ya sea con su nombre original o el nuevo nombre).
            try:
                # Mostrar información sobre conflictos de nombres
                if ruta_archivo_destino != os.path.join(directorio_destino_actual, filename_convertido):
                    print(f"  -> Conflicto detectado para '{filename_convertido}'. Renombrando a '{os.path.basename(ruta_archivo_destino)}'")
                
                # Si tenemos contenido limpio (sin shebang o sin tags XML), escribirlo directamente
                if contenido_limpio is not None:
                    with open(ruta_archivo_destino, 'w', encoding='utf-8') as archivo_destino:
                        archivo_destino.write(contenido_limpio)
                else:
                    # Copiar archivo normalmente
                    shutil.copy2(ruta_archivo_original, ruta_archivo_destino)
                
                archivos_copiados += 1
                
                # Mostrar progreso cada 50 archivos
                if archivos_copiados % 50 == 0:
                    print(f"  -> Progreso: {archivos_copiados} archivos copiados")
                    
            except Exception as e:
                print(f"  !! Error al copiar {ruta_archivo_original}: {e}")

    print(f"\n¡Proceso completado!")
    print(f"Total de archivos copiados: {archivos_copiados}")
    print(f"Total de imágenes copiadas: {imagenes_copiadas}")
    print(f"Total de carpetas de archivos creadas: {carpeta_actual}")
    print(f"Total de carpetas de imágenes creadas: {carpeta_imagenes_actual}")
    
    if carpeta_actual > 1:
        print(f"Carpetas de archivos: {destino} (carpeta principal) y {carpeta_actual - 1} carpetas adicionales (carpeta_2 hasta carpeta_{carpeta_actual})")
    else:
        print(f"Todos los archivos se copiaron en: {destino}")
    
    if carpeta_imagenes_actual > 1:
        print(f"Carpetas de imágenes: imagenes_1 hasta imagenes_{carpeta_imagenes_actual} (máximo {MAX_IMAGENES_PER_FOLDER} imágenes por carpeta)")
    else:
        print(f"Imágenes copiadas en: imagenes_1")
    
    # Eliminar archivos vacíos después del proceso
    eliminar_archivos_vacios(destino)


# --- Ejecutar la función ---
if __name__ == "__main__":
    import sys
    
    # Verificar si se quiere solo eliminar archivos vacíos
    if len(sys.argv) > 1 and sys.argv[1] == "--eliminar-vacios":
        print("Modo: Solo eliminar archivos vacíos")
        if os.path.isdir(ruta_destino):
            eliminar_archivos_vacios(ruta_destino)
        else:
            print(f"Error: La ruta de destino '{ruta_destino}' no existe.")
    else:
        # Validaciones básicas para el proceso normal
        if not os.path.isdir(ruta_origen):
            print(f"Error: La ruta de origen '{ruta_origen}' no existe o no es un directorio.")
        elif ruta_origen == ruta_destino:
             print("Error: La ruta de origen y destino no pueden ser la misma.")
        else:
            aplanar_directorio(ruta_origen, ruta_destino)
