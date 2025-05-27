def download_stormlib_dll():
    import urllib.request
    import zipfile
    import io
    import platform
    from pathlib import Path

    STORMLIB_URL = "https://github.com/ladislav-zezula/StormLib/releases/download/v9.30/stormlib_dll.zip"
    arch = "x64" if platform.architecture()[0] == "64bit" else "Win32"
    dll_name = "StormLib.dll"
    subpath = f"{arch}/{dll_name}"

    print(f"Downloading StormLib ({arch}) from the StormLib Github repo...")
    dest = Path(__file__).parent / "lib"
    dest.mkdir(parents=True, exist_ok=True)

    with urllib.request.urlopen(STORMLIB_URL) as resp:
        with zipfile.ZipFile(io.BytesIO(resp.read())) as z:
            try:
                dll_data = z.read(subpath)
            except KeyError:
                raise RuntimeError(f"{subpath} not found in archive")

            dll_path = dest / dll_name
            with open(dll_path, "wb") as f:
                f.write(dll_data)

    exit(f"Extracted {dll_name} to: {dll_path.resolve()}")


from ._stormlib import stormlib, MPQFileFlags, SFileFindDataStrc
from .mpq import MPQArchive
