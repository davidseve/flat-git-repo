# Flatten Directory - File Reorganization Script

This Python script allows you to "flatten" directory structures by copying all files from a source directory (with multiple subdirectories) to a destination directory, organizing them into folders with size and file count limits.

## 🎯 Purpose

The script is designed to:
- Copy files from a complex directory structure to a simpler one
- Organize files into folders with controlled limits
- Separate images into dedicated folders
- Convert non-allowed file extensions to valid extensions
- Clean specific content (like shebangs in shell scripts)
- Automatically remove empty files

## 📋 Requirements

- Python 3.6 or higher
- Read permissions on the source directory
- Write permissions on the destination directory

## ⚙️ Configuration

### Method 1: Command Line Parameters (Recommended)

You can specify the source and destination paths directly as command line parameters:

```bash
python aplanar_directorio.py /path/to/source /path/to/destination
```

### Method 2: Default Configuration

Alternatively, you can modify the default paths in the `aplanar_directorio.py` file:

```python
# Default paths (can be overridden with command line parameters)
ruta_origen_default = "/path/to/your/source/project"
ruta_destino_default = "/path/to/your/destination/project"
```

### Configurable Limits

The script includes several limits that you can adjust according to your needs:

```python
MAX_FILE_SIZE_MB = 200          # Maximum size per file in MB
MAX_WORDS_PER_FILE = 500000     # Maximum words per file
MAX_FILES_PER_FOLDER = 300      # Maximum files per folder
MAX_IMAGENES_PER_FOLDER = 10    # Maximum images per folder
```

## 🚀 Usage

### Command Line Syntax

```bash
python aplanar_directorio.py [OPTIONS] [SOURCE] [DESTINATION]
```

### Options

- `-h, --help` - Show help information
- `--eliminar-vacios` - Only remove empty files from destination directory

### Parameters

- `SOURCE` - Path to source directory (optional, uses default if not specified)
- `DESTINATION` - Path to destination directory (optional, uses default if not specified)

### Usage Examples

#### Use Default Paths
```bash
python aplanar_directorio.py
```

#### Specify Only Source Path
```bash
python aplanar_directorio.py /path/to/source
```

#### Specify Both Source and Destination
```bash
python aplanar_directorio.py /path/to/source /path/to/destination
```

#### Remove Only Empty Files
```bash
python aplanar_directorio.py --eliminar-vacios /path/to/destination
```

#### Show Help
```bash
python aplanar_directorio.py --help
```

### Notes

- If SOURCE is not specified, the default path is used
- If DESTINATION is not specified, the default path is used
- Source and destination paths must be different
- The destination directory will be created automatically if it doesn't exist

## 📁 Output Structure

The script organizes files in the following way:

```
destination_directory/
├── carpeta_1/              # Regular files (maximum 300 per folder)
│   ├── file1.txt
│   ├── file2.md
│   └── ...
├── carpeta_2/              # New folder when limit is reached
│   └── ...
├── imagenes_1/             # Images (maximum 10 per folder)
│   ├── image1.png
│   ├── image2.jpg
│   └── ...
└── imagenes_2/             # New image folder when limit is reached
    └── ...
```

## 🔧 Features

### Allowed Extensions

The script processes files with the following extensions:
- **Documents**: `pdf`, `txt`, `md`
- **Audio**: `aac`, `mp3`, `wav`, `ogg`, etc.
- **Video**: `avi`, `mp4`, `mpeg`, etc.
- **Images**: `png`, `jpg`, `gif`, `svg`, etc.

### Extension Conversion

Files with non-allowed extensions are automatically converted:
- Scripts (`.sh`, `.py`, `.js`) → `.txt` or `.md`
- Configuration (`.yaml`, `.json`, `.xml`) → `.txt`
- Documentation (`.adoc`, `.rst`) → `.txt`
- And many more...

### Excluded Files

The following file types are automatically excluded:
- Fonts: `.ttf`, `.otf`, `.woff`, `.woff2`, `.eot`
- `.git` directory (complete)

### Content Cleaning

- **Shell Scripts**: Automatically removes shebang lines (`#!/bin/bash`, etc.)
- **Empty Files**: Automatically removed at the end of the process

### Conflict Handling

- If a file with the same name exists, a numeric suffix is added (`_1`, `_2`, etc.)
- Each detected conflict is reported

## 📊 Progress Information

The script provides detailed information during execution:

```
Searching files in: /source/path
Copying files to: /destination/path
Limits: 200 MB per file, 500,000 words per file, 300 files per folder

Creating initial folder: /destination/path
Creating image folder: /destination/path/imagenes_1
  -> Extension conversion: '.sh' → '.md' (file: script.sh)
  -> Shebang removed from: script.sh
  -> File copied: script.md
  -> Progress: 50 files copied
  ...

Process completed!
Total files copied: 1,234
Total images copied: 45
Total file folders created: 5
Total image folders created: 5
```

## ⚠️ Important Considerations

1. **Different Paths**: Source and destination paths must be different
2. **Disk Space**: Make sure you have enough space to duplicate the files
3. **Permissions**: Verify you have read/write permissions on both locations
4. **Backup**: Consider making a backup before running the script
5. **Large Files**: Files larger than 200 MB are automatically skipped

## 🐛 Troubleshooting

### Error: "Source path does not exist"
- Verify that the path configured in `ruta_origen` is correct
- Make sure the directory exists and you have read permissions

### Error: "Source and destination paths cannot be the same"
- Change the `ruta_destino` configuration to a different location

### Files not copied
- Verify that extensions are in the allowed extensions list
- Check the configured size and word limits
- Review error messages in the script output

## 📝 Configuration Examples

### Command Line Usage Examples

```bash
# Process a specific project
python aplanar_directorio.py /home/user/my-project /home/user/my-project-flat

# Process with only source specified (uses default destination)
python aplanar_directorio.py /home/user/my-project

# Clean empty files from a specific directory
python aplanar_directorio.py --eliminar-vacios /home/user/my-project-flat
```

### Default Configuration Example

```python
# Example default configuration in the script
ruta_origen_default = "/home/user/my-project"
ruta_destino_default = "/home/user/my-project-flat"

# More conservative limits for large projects
MAX_FILE_SIZE_MB = 100
MAX_WORDS_PER_FILE = 100000
MAX_FILES_PER_FOLDER = 200
MAX_IMAGENES_PER_FOLDER = 5
```

## 🤝 Contributions

If you find any issues or have improvement suggestions, you can:
1. Report the problem with specific details
2. Propose functionality improvements
3. Suggest new file extensions for the mapping

---

**Note**: This script is designed to reorganize files safely, but it's always recommended to make a backup before running it on important directories.
