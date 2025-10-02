import os
import shutil
import subprocess
import tempfile

# --- CONFIGURATION ---
# Default paths (can be overridden with command line parameters)

# Path to your original project folder (the one with many subfolders).
ruta_origen_default = "/home/dseveria/hack/ocp-gitops-architecture"

# Path to the empty folder you created to save all files.
ruta_destino_default = "/home/dseveria/hack/ocp-gitops-architecture-flat"

# Git repository URL (optional)
git_repo_default = None

# Allowed file extensions
EXTENSIONES_PERMITIDAS = {
    'pdf', 'txt', 'md', '3g2', '3gp', 'aac', 'aif', 'aifc', 'aiff', 'amr', 
    'au', 'avi', 'cda', 'm4a', 'mid', 'mp3', 'mp4', 'mpeg', 'ogg', 'opus', 
    'ra', 'ram', 'snd', 'wav', 'wma'
}

# Control limits
MAX_FILE_SIZE_MB = 200  # Maximum size per file in MB
MAX_WORDS_PER_FILE = 500000  # Maximum words per file
MAX_FILES_PER_FOLDER = 300  # Maximum files per folder
MAX_IMAGENES_PER_FOLDER = 10  # Maximum images per folder

# Image extensions that will be copied to separate folder
EXTENSIONES_IMAGENES = {
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'ico', 'tiff', 'webp', 'tga', 'psd', 'ai', 'eps', 'xcf', 'graphml'
}
# ---------------------


def es_extension_permitida(extension):
    """
    Checks if the file extension is in the list of allowed extensions.
    """
    return extension.lower().lstrip('.') in EXTENSIONES_PERMITIDAS


def es_imagen(extension):
    """
    Checks if the file extension corresponds to an image.
    """
    return extension.lower().lstrip('.') in EXTENSIONES_IMAGENES


def es_archivo_excluido(extension):
    """
    Checks if the file extension should be excluded from processing.
    """
    extensiones_excluidas = {'ttf', 'otf', 'woff', 'woff2', 'eot', 'jar', 'war', 'zip', 'tar', 'gz', 'bz2', 'rar', '7z'}  # Fonts
    return extension.lower().lstrip('.') in extensiones_excluidas


def limpiar_shebang_shell(ruta_archivo):
    """
    Reads a shell script file and removes the shebang line (#!/bin/bash, #!/bin/sh, etc.)
    Returns the clean content or None if there's an error.
    """
    try:
        # Try to read with different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(ruta_archivo, 'r', encoding=encoding) as archivo:
                    lineas = archivo.readlines()
                
                # Filter lines that start with #!/ (shebang)
                lineas_limpias = []
                for linea in lineas:
                    linea_stripped = linea.strip()
                    # Remove any line that starts with #!/
                    if not linea_stripped.startswith('#!/'):
                        lineas_limpias.append(linea)
                
                return ''.join(lineas_limpias)
                
            except UnicodeDecodeError:
                continue
        
        # If it cannot be read as text, return None
        return None
        
    except Exception as e:
        print(f"  !! Error al limpiar shebang de {ruta_archivo}: {e}")
        return None




def verificar_tamaño_archivo(ruta_archivo):
    """
    Checks if the file does not exceed the maximum allowed size.
    Returns True if the file is valid, False if it's too large.
    """
    try:
        tamaño_bytes = os.path.getsize(ruta_archivo)
        tamaño_mb = tamaño_bytes / (1024 * 1024)  # Convert to MB
        
        if tamaño_mb > MAX_FILE_SIZE_MB:
            print(f"  !! Archivo demasiado grande ({tamaño_mb:.2f} MB > {MAX_FILE_SIZE_MB} MB): {ruta_archivo}")
            return False
        return True
    except Exception as e:
        print(f"  !! Error al verificar tamaño de {ruta_archivo}: {e}")
        return False


def contar_palabras_archivo(ruta_archivo):
    """
    Counts words in a text file.
    Returns the number of words or -1 if there's an error.
    """
    try:
        # Try to read as text with different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(ruta_archivo, 'r', encoding=encoding) as archivo:
                    contenido = archivo.read()
                    # Count words separated by spaces, line breaks, etc.
                    palabras = len(contenido.split())
                    return palabras
            except UnicodeDecodeError:
                continue
        
        # If it cannot be read as text, assume it's binary and count bytes
        with open(ruta_archivo, 'rb') as archivo:
            contenido = archivo.read()
            # For binary files, estimate words based on size
            # Assuming ~5 characters per word on average
            palabras_estimadas = len(contenido) // 5
            return palabras_estimadas
            
    except Exception as e:
        print(f"  !! Error al contar palabras en {ruta_archivo}: {e}")
        return -1


def verificar_palabras_archivo(ruta_archivo):
    """
    Checks if the file does not exceed the word limit.
    Returns True if the file is valid, False if it has too many words.
    """
    palabras = contar_palabras_archivo(ruta_archivo)
    
    if palabras == -1:  # Error reading the file
        return False
    
    if palabras > MAX_WORDS_PER_FILE:
        print(f"  !! Archivo con demasiadas palabras ({palabras:,} > {MAX_WORDS_PER_FILE:,}): {ruta_archivo}")
        return False
    
    return True


def clonar_repositorio_git(git_url, directorio_destino):
    """
    Clones a Git repository to the specified directory.
    Uses GitLab PAT from environment variable if available.
    """
    try:
        # Check if GitLab PAT is available
        gitlab_pat = os.environ.get('GITLAB_PAT')
        
        if gitlab_pat:
            print(f"Using GitLab PAT for authentication")
            # Modify URL to include PAT for authentication
            if 'gitlab.com' in git_url or '@' in git_url:
                # Handle different GitLab URL formats
                if git_url.startswith('https://'):
                    # Replace https:// with https://oauth2:TOKEN@
                    git_url_auth = git_url.replace('https://', f'https://oauth2:{gitlab_pat}@')
                elif git_url.startswith('git@'):
                    # For SSH URLs, we'll use HTTPS with PAT instead
                    git_url_auth = git_url.replace('git@gitlab.com:', f'https://oauth2:{gitlab_pat}@gitlab.com/')
                else:
                    git_url_auth = git_url
            else:
                git_url_auth = git_url
        else:
            print(f"Warning: GITLAB_PAT environment variable not set. Using public access.")
            git_url_auth = git_url
        
        print(f"Cloning repository: {git_url}")
        print(f"Destination: {directorio_destino}")
        
        # Clone the repository
        result = subprocess.run([
            'git', 'clone', '--depth', '1', git_url_auth, directorio_destino
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"Repository cloned successfully to: {directorio_destino}")
            return True
        else:
            print(f"Error cloning repository:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"Error: Git clone operation timed out")
        return False
    except Exception as e:
        print(f"Error cloning repository: {e}")
        return False


def verificar_git_disponible():
    """
    Checks if Git is available in the system.
    """
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Git available: {result.stdout.strip()}")
            return True
        else:
            print("Error: Git is not available in the system")
            return False
    except FileNotFoundError:
        print("Error: Git is not installed or not in PATH")
        return False


def eliminar_archivos_vacios(directorio):
    """
    Removes all empty files (0 bytes) from the specified directory.
    """
    archivos_eliminados = 0
    
    print(f"\nSearching for empty files in: {directorio}")
    
    for dirpath, _, filenames in os.walk(directorio):
        for filename in filenames:
            ruta_archivo = os.path.join(dirpath, filename)
            
            try:
                # Verificar si el archivo está vacío
                if os.path.getsize(ruta_archivo) == 0:
                    print(f"  -> Removing empty file: {ruta_archivo}")
                    os.remove(ruta_archivo)
                    archivos_eliminados += 1
            except Exception as e:
                print(f"  !! Error al procesar {ruta_archivo}: {e}")
    
    print(f"Total empty files removed: {archivos_eliminados}")
    return archivos_eliminados


def convertir_extension_a_txt(filename):
    """
    Converts a file extension to a valid extension similar to the original type.
    Shows the original type and the transformation applied.
    """
    nombre_base, extension = os.path.splitext(filename)
    extension_lower = extension.lower()
    
    # If it has no extension, add .txt
    if not extension:
        nuevo_nombre = f"{nombre_base}.txt"
        print(f"  -> Adding extension: no extension → '.txt' (file: {filename})")
        return nuevo_nombre
    
    # Mapping of extensions to more similar valid extensions
    mapeo_extensiones = {
        # Scripts and code
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
        
        # Configuration and data
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
        
        # Documentation
        '.adoc': '.txt',        # AsciiDoc → Texto
        '.rst': '.txt',         # reStructuredText → Texto
        '.tex': '.txt',         # LaTeX → Texto
        '.org': '.txt',         # Org mode → Texto
        
        # Templates and others
        '.template': '.txt',    # Template → Texto
        '.tpl': '.txt',         # Template → Texto
        '.mustache': '.txt',    # Mustache → Texto
        '.hbs': '.txt',         # Handlebars → Texto
        '.ejs': '.txt',         # EJS → Texto
        
        # Docker and containers
        '.dockerfile': '.txt',  # Dockerfile → Texto
        '.dockerignore': '.txt', # Docker ignore → Texto
        
        # Other text files
        '.log': '.txt',         # Log files → Texto
        '.sql': '.txt',         # SQL → Texto
        '.diff': '.txt',        # Diff → Texto
        '.patch': '.txt',       # Patch → Texto
        '.gitignore': '.txt',   # Git ignore → Texto
        '.gitattributes': '.txt', # Git attributes → Texto
        
        # Images are handled separately, not included here
        
        # Diagrams and design
        '.excalidraw': '.txt',  # Excalidraw → Texto
        '.drawio': '.txt',      # Draw.io → Texto
        '.vsdx': '.txt',        # Visio → Texto
        '.dwg': '.txt',         # AutoCAD → Texto
        
        # Compressed files (convert to descriptive text)
        '.zip': '.txt',         # ZIP → Texto
        '.tar': '.txt',         # TAR → Texto
        '.gz': '.txt',          # GZIP → Texto
        '.rar': '.txt',         # RAR → Texto
        '.7z': '.txt',          # 7-Zip → Texto
        
        # Binaries (convert to descriptive text)
        '.exe': '.txt',         # Executable → Texto
        '.dll': '.txt',         # DLL → Texto
        '.so': '.txt',          # Shared Object → Texto
        '.dylib': '.txt',       # Dynamic Library → Texto
        '.bin': '.txt',         # Binary → Texto
    }
    
    # If the extension is allowed, do nothing
    if es_extension_permitida(extension):
        return filename
    
    # Search in the mapping
    if extension_lower in mapeo_extensiones:
        nueva_extension = mapeo_extensiones[extension_lower]
        nuevo_nombre = f"{nombre_base}{nueva_extension}"
        print(f"  -> Extension conversion: '{extension}' → '{nueva_extension}' (file: {filename})")
        return nuevo_nombre
    
    # If not in the mapping, use .txt as fallback
    nuevo_nombre = f"{nombre_base}.txt"
    print(f"  -> Extension conversion: '{extension}' → '.txt' (fallback, file: {filename})")
    return nuevo_nombre


def aplanar_directorio(origen, destino):
    """
    Copies all files from a source directory and its subdirectories
    to destination directories, handling name conflicts and size controls.
    """
    # 1. Make sure the base destination folder exists.
    if not os.path.exists(destino):
        print(f"Creating destination directory: {destino}")
        os.makedirs(destino)

    print(f"Searching files in: {origen}")
    print(f"Copying files to: {destino}")
    print(f"Limits: {MAX_FILE_SIZE_MB} MB per file, {MAX_WORDS_PER_FILE:,} words per file, {MAX_FILES_PER_FOLDER} files per folder\n")

    # Counters for multiple folder control
    archivos_copiados = 0
    imagenes_copiadas = 0
    carpeta_actual = 1
    carpeta_imagenes_actual = 1
    directorio_destino_actual = destino
    
    # Create the first folder if necessary
    if not os.path.exists(directorio_destino_actual):
        print(f"Creating initial folder: {directorio_destino_actual}")
        os.makedirs(directorio_destino_actual)
    
    # Create first folder for images
    directorio_imagenes_actual = os.path.join(destino, f"imagenes_{carpeta_imagenes_actual}")
    if not os.path.exists(directorio_imagenes_actual):
        print(f"Creating folder for images: {directorio_imagenes_actual}")
        os.makedirs(directorio_imagenes_actual)
    
    # 2. Traverse each folder, subfolder and file in the source.
    for dirpath, _, filenames in os.walk(origen):
        # Ignore the .git directory completely
        if ".git" in dirpath.split(os.sep):
            continue
            
        for filename in filenames:
            # Build the complete path of the original file
            ruta_archivo_original = os.path.join(dirpath, filename)
            
            # Get the file extension
            _, extension = os.path.splitext(filename)
            
            # 3. Check if the file should be excluded
            if es_archivo_excluido(extension):
                print(f"  -> Excluded file (extension {extension}): {filename}")
                continue
            
            # 4. Check file size
            if not verificar_tamaño_archivo(ruta_archivo_original):
                continue
            
            # 4.5. If it has no extension, check that it has content before adding .txt
            if not extension:
                try:
                    # Check if the file has content (is not empty)
                    if os.path.getsize(ruta_archivo_original) == 0:
                        print(f"  -> File without extension and empty, skipping: {filename}")
                        continue
                except Exception as e:
                    print(f"  !! Error al verificar archivo sin extensión {ruta_archivo_original}: {e}")
                    continue
            
            # 5. Check if it's an image
            if es_imagen(extension):
                # Create new image folder if limit is reached
                if imagenes_copiadas > 0 and imagenes_copiadas % MAX_IMAGENES_PER_FOLDER == 0:
                    carpeta_imagenes_actual += 1
                    directorio_imagenes_actual = os.path.join(destino, f"imagenes_{carpeta_imagenes_actual}")
                    if not os.path.exists(directorio_imagenes_actual):
                        print(f"Creating new image folder: {directorio_imagenes_actual}")
                        os.makedirs(directorio_imagenes_actual)
                
                # Handle images separately
                ruta_imagen_destino = os.path.join(directorio_imagenes_actual, filename)
                
                # Conflict handling for images
                contador = 1
                nombre_base, ext = os.path.splitext(filename)
                
                while os.path.exists(ruta_imagen_destino):
                    nuevo_nombre = f"{nombre_base}_{contador}{ext}"
                    ruta_imagen_destino = os.path.join(directorio_imagenes_actual, nuevo_nombre)
                    contador += 1
                
                try:
                    if ruta_imagen_destino != os.path.join(directorio_imagenes_actual, filename):
                        print(f"  -> Conflict detected for image '{filename}'. Renaming to '{os.path.basename(ruta_imagen_destino)}'")
                    
                    shutil.copy2(ruta_archivo_original, ruta_imagen_destino)
                    imagenes_copiadas += 1
                    print(f"  -> Image copied: {filename} (folder imagenes_{carpeta_imagenes_actual})")
                    
                except Exception as e:
                    print(f"  !! Error al copiar imagen {ruta_archivo_original}: {e}")
                
                continue
            
            # 6. Check file word count (only for non-image files)
            if not verificar_palabras_archivo(ruta_archivo_original):
                continue
            
            # 7. Create new folder if file limit is reached
            if archivos_copiados > 0 and archivos_copiados % MAX_FILES_PER_FOLDER == 0:
                carpeta_actual += 1
                directorio_destino_actual = os.path.join(destino, f"carpeta_{carpeta_actual}")
                if not os.path.exists(directorio_destino_actual):
                    print(f"Creando nueva carpeta: {directorio_destino_actual}")
                    os.makedirs(directorio_destino_actual)
            
            # Convert extension if not allowed
            filename_convertido = convertir_extension_a_txt(filename)
            
            # Build tentative path in destination
            ruta_archivo_destino = os.path.join(directorio_destino_actual, filename_convertido)
            
            # Process special content according to file type
            contenido_limpio = None
            
            # If it's a .sh file converted to .md, clean the shebang
            if filename_convertido.endswith('.md') and (filename.endswith('.sh') or filename.endswith('.bash')):
                contenido_limpio = limpiar_shebang_shell(ruta_archivo_original)
                if contenido_limpio is not None:
                    print(f"  -> Shebang removed from: {filename}")
            
           
            
            # 8. Conflict handling: check if a file with that name already exists.
            contador = 1
            nombre_base, extension = os.path.splitext(filename_convertido)
            
            while os.path.exists(ruta_archivo_destino):
                # If it exists, create a new name with a numeric suffix
                nuevo_nombre = f"{nombre_base}_{contador}{extension}"
                ruta_archivo_destino = os.path.join(directorio_destino_actual, nuevo_nombre)
                contador += 1

            # 9. Copy the file (either with its original name or the new name).
            try:
                # Show information about name conflicts
                if ruta_archivo_destino != os.path.join(directorio_destino_actual, filename_convertido):
                    print(f"  -> Conflict detected for '{filename_convertido}'. Renaming to '{os.path.basename(ruta_archivo_destino)}'")
                
                # If we have clean content (without shebang or XML tags), write it directly
                if contenido_limpio is not None:
                    with open(ruta_archivo_destino, 'w', encoding='utf-8') as archivo_destino:
                        archivo_destino.write(contenido_limpio)
                else:
                    # Copy file normally
                    shutil.copy2(ruta_archivo_original, ruta_archivo_destino)
                
                archivos_copiados += 1
                
                # Show progress every 50 files
                if archivos_copiados % 50 == 0:
                    print(f"  -> Progress: {archivos_copiados} files copied")
                    
            except Exception as e:
                print(f"  !! Error al copiar {ruta_archivo_original}: {e}")

    print(f"\nProcess completed!")
    print(f"Total files copied: {archivos_copiados}")
    print(f"Total images copied: {imagenes_copiadas}")
    print(f"Total file folders created: {carpeta_actual}")
    print(f"Total image folders created: {carpeta_imagenes_actual}")
    
    if carpeta_actual > 1:
        print(f"File folders: {destino} (main folder) and {carpeta_actual - 1} additional folders (carpeta_2 to carpeta_{carpeta_actual})")
    else:
        print(f"All files were copied to: {destino}")
    
    if carpeta_imagenes_actual > 1:
        print(f"Image folders: imagenes_1 to imagenes_{carpeta_imagenes_actual} (maximum {MAX_IMAGENES_PER_FOLDER} images per folder)")
    else:
        print(f"Images copied to: imagenes_1")
    
    # Remove empty files after the process
    eliminar_archivos_vacios(destino)


def mostrar_ayuda():
    """
    Shows the script help information.
    """
    print("""
Flatten Directory - File Reorganization Script

USAGE:
    python aplanar_directorio.py [OPTIONS] [SOURCE] [DESTINATION] [GIT_REPO]

OPTIONS:
    -h, --help              Show this help
    --eliminar-vacios       Only remove empty files from destination directory
    --git-clone             Clone Git repository before processing

PARAMETERS:
    SOURCE                  Path to source directory (optional, uses default value if not specified)
    DESTINATION             Path to destination directory (optional, uses default value if not specified)
    GIT_REPO                Git repository URL (optional, requires --git-clone option)

EXAMPLES:
    # Use default paths
    python aplanar_directorio.py
    
    # Specify only source
    python aplanar_directorio.py /path/source
    
    # Specify source and destination
    python aplanar_directorio.py /path/source /path/destination
    
    # Clone Git repository and process it
    python aplanar_directorio.py --git-clone https://gitlab.com/user/repo.git /path/destination
    
    # Clone Git repository with custom source name
    python aplanar_directorio.py --git-clone https://gitlab.com/user/repo.git /path/source /path/destination
    
    # Only remove empty files
    python aplanar_directorio.py --eliminar-vacios /path/destination
    
    # Show help
    python aplanar_directorio.py --help

GIT INTEGRATION:
    - Set GITLAB_PAT environment variable for GitLab authentication
    - Supports both HTTPS and SSH Git URLs
    - Uses shallow clone (--depth 1) for faster cloning
    - Automatically handles GitLab PAT authentication

NOTES:
    - If SOURCE is not specified, uses: {ruta_origen_default}
    - If DESTINATION is not specified, uses: {ruta_destino_default}
    - Source and destination paths must be different
    - The destination directory will be created automatically if it doesn't exist
    - Git repository will be cloned to a temporary directory when using --git-clone
    """.format(
        ruta_origen_default=ruta_origen_default,
        ruta_destino_default=ruta_destino_default
    ))


def parsear_argumentos():
    """
    Parses command line arguments and returns paths and options.
    """
    import sys
    
    # Default values
    origen = ruta_origen_default
    destino = ruta_destino_default
    git_repo = git_repo_default
    solo_eliminar_vacios = False
    directorio_eliminar_vacios = None
    usar_git_clone = False
    
    # Counter to track how many path parameters we have processed
    parametros_ruta = 0
    
    # Process arguments
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg in ['-h', '--help']:
            mostrar_ayuda()
            sys.exit(0)
        elif arg == '--eliminar-vacios':
            solo_eliminar_vacios = True
            # The next argument should be the destination directory
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('-'):
                directorio_eliminar_vacios = sys.argv[i + 1]
                i += 1
            else:
                directorio_eliminar_vacios = destino
        elif arg == '--git-clone':
            usar_git_clone = True
        elif not arg.startswith('-'):
            # It's a path parameter
            if usar_git_clone and parametros_ruta == 0:
                # First parameter after --git-clone is the Git repository URL
                git_repo = arg
                parametros_ruta += 1
            elif parametros_ruta == 0:
                origen = arg
                parametros_ruta += 1
            elif parametros_ruta == 1:
                destino = arg
                parametros_ruta += 1
            else:
                print(f"Error: Too many parameters. Unexpected argument: {arg}")
                print("Use --help to see help.")
                sys.exit(1)
        else:
            print(f"Error: Unknown option: {arg}")
            print("Use --help to see help.")
            sys.exit(1)
        
        i += 1
    
    return origen, destino, git_repo, solo_eliminar_vacios, directorio_eliminar_vacios, usar_git_clone


# --- Execute the function ---
if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    ruta_origen, ruta_destino, git_repo, solo_eliminar_vacios, directorio_eliminar_vacios, usar_git_clone = parsear_argumentos()
    
    # Check if we only want to remove empty files
    if solo_eliminar_vacios:
        print("Mode: Only remove empty files")
        directorio_a_limpiar = directorio_eliminar_vacios or ruta_destino
        if os.path.isdir(directorio_a_limpiar):
            eliminar_archivos_vacios(directorio_a_limpiar)
        else:
            print(f"Error: The destination path '{directorio_a_limpiar}' does not exist.")
    else:
        # Handle Git clone functionality
        if usar_git_clone:
            if not git_repo:
                print("Error: --git-clone option requires a Git repository URL")
                print("Use --help to see help.")
                sys.exit(1)
            
            # Check if Git is available
            if not verificar_git_disponible():
                print("Error: Git is required for --git-clone functionality")
                sys.exit(1)
            
            # Create temporary directory for Git clone
            temp_dir = tempfile.mkdtemp(prefix="git_clone_")
            print(f"Using temporary directory for Git clone: {temp_dir}")
            
            # Clone the repository
            if clonar_repositorio_git(git_repo, temp_dir):
                # Use the cloned repository as source
                ruta_origen = temp_dir
                print(f"Git repository cloned successfully. Processing from: {ruta_origen}")
            else:
                print("Error: Failed to clone Git repository")
                # Clean up temporary directory
                shutil.rmtree(temp_dir, ignore_errors=True)
                sys.exit(1)
        
        # Basic validations for normal process
        if not os.path.isdir(ruta_origen):
            print(f"Error: The source path '{ruta_origen}' does not exist or is not a directory.")
        elif ruta_origen == ruta_destino:
             print("Error: Source and destination paths cannot be the same.")
        else:
            try:
                aplanar_directorio(ruta_origen, ruta_destino)
            finally:
                # Clean up temporary directory if we used Git clone
                if usar_git_clone and 'temp_dir' in locals():
                    print(f"Cleaning up temporary directory: {temp_dir}")
                    shutil.rmtree(temp_dir, ignore_errors=True)
