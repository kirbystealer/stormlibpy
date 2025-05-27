# StormLibPy

**StormLibPy** is a Python wrapper around [StormLib](https://github.com/ladislav-zezula/StormLib), a C library for reading and writing Blizzard's MPQ archives. This wrapper uses `ctypes` to provide an interface for opening, extracting, modifying, and creating MPQ archives on Windows.

---

## Features

- List files in MPQ (including anonymous files)
- Read files from MPQ by filename
- Write existing files to MPQ from local disk
- Write in-memory files to MPQ
- Delete files from MPQ
- Compact (resize) MPQ

## Installation

### Prerequisites

- Python 3.7+
- Windows

### Install via pip (from GitHub)

`pip install git+https://github.com/kirbystealer/StormLibPy.git`

### StormLib.dll
You will need the appropriate `StormLib.dll` for your architecture. 
It should go in a directory as `lib\StormLib.dll`.
This wrapper was developed on v9.30 (64-bit build)

You can install it via these options:

#### Option 1
Install `stormlibpy` via pip, then run `python -c "import stormlibpy"` to get a download prompt:
```commandline
python -c "import stormlibpy"
Could't find StormLib.dll at .venv\Lib\site-packages\stormlibpy\lib\StormLib.dll. Should we download it, Y/N?Y
Downloading StormLib (x64) from the StormLib Github repo...
Extracted StormLib.dll to: .venv\Lib\site-packages\stormlibpy\lib\StormLib.dll
```

#### Option 2
You can build the library from source or get the prebuilt release at:  
https://github.com/ladislav-zezula/StormLib/releases.   


## Example Usage

```python
from stormlibpy import MPQArchive

with MPQArchive("path/to/your/war3map.w3x") as archive:
    # Print a list of filenames in the archive
    files = archive.list_files()    
    print(files)

    # Read a file from the archive
    data = archive.read_file("war3map.j")
    print(data.decode())

    # Add a file from local disk
    filepath = "path/to/your/war3map.j"
    archive.add_file(filepath, archived_name="war3map.j")      
    
    # Delete the file we just added.
    archive.remove_file("war3map.j")
    
    # Squashes the archive. Won't work on archives with incomplete listfiles
    archive.compact()
    
    # Save the archive. This closes any open handles and overwrites 
    # the existing archive with your modified one.
    archive.save()
 ```

To see the full list of supported `StormLib` functions or to add new ones, check out `_stormlib.py`

## Future Work
- Make cross-platform compatible?
- Support all existing StormLib API functions.