import ctypes
import ctypes.wintypes
import enum
import pathlib


# fmt:off
class MPQFileFlags(enum.IntFlag):
    MPQ_FILE_IMPLODE            = 0x00000100
    MPQ_FILE_COMPRESS           = 0x00000200
    MPQ_FILE_ENCRYPTED          = 0x00010000
    MPQ_FILE_FIX_KEY            = 0x00020000
    MPQ_FILE_DELETE_MARKER      = 0x02000000
    MPQ_FILE_SECTOR_CRC         = 0x04000000
    MPQ_FILE_SINGLE_UNIT        = 0x10000000
    MPQ_FILE_REPLACEEXISTING    = 0x80000000

    MPQ_COMPRESSION_HUFFMANN     = 0x01
    MPQ_COMPRESSION_ZLIB         = 0x02
    MPQ_COMPRESSION_PKWARE       = 0x08
    MPQ_COMPRESSION_BZIP2        = 0x10
    MPQ_COMPRESSION_SPARSE       = 0x20
    MPQ_COMPRESSION_ADPCM_MONO   = 0x40
    MPQ_COMPRESSION_ADPCM_STEREO = 0x80
    MPQ_COMPRESSION_LZMA         = 0x12
    MPQ_COMPRESSION_NEXT_SAME    = 0xFFFFFFFF
# fmt:om

class SFileFindDataStrc(ctypes.Structure):
    MAX_PATH = 260
    _fields_ = [
        ("cFileName", ctypes.c_char * MAX_PATH),
        ("szPlainName", ctypes.c_char_p),
        ("dwHashIndex", ctypes.wintypes.DWORD),
        ("dwBlockIndex", ctypes.wintypes.DWORD),
        ("dwFileSize", ctypes.wintypes.DWORD),
        ("dwFileFlags", ctypes.wintypes.DWORD),
        ("dwCompSize", ctypes.wintypes.DWORD),
        ("dwFileTimeLo", ctypes.wintypes.DWORD),
        ("dwFileTimeHi", ctypes.wintypes.DWORD),
        ("lcLocale", ctypes.wintypes.LCID),
    ]


STORMLIB_PATH = pathlib.Path(__file__).parent.joinpath("lib", "StormLib.dll")
try:
    stormlib = ctypes.WinDLL(str(STORMLIB_PATH))
except FileNotFoundError:
    if not pathlib.Path(STORMLIB_PATH).exists():
        download = input(
            f"Could't find StormLib.dll at {STORMLIB_PATH}. Should we download it, Y/N? "
        )
        if download.lower() in ["yes", "y"]:
            import stormlibpy

            stormlibpy.download_stormlib_dll()


##################################################################################################
# Function signatures from https://github.com/ladislav-zezula/StormLib/blob/master/src/StormLib.h
##################################################################################################
stormlib.GetLastError.restype = ctypes.c_uint32

# LCID   WINAPI SFileSetLocale(LCID lcFileLocale)
stormlib.SFileSetLocale.argtypes = [ctypes.wintypes.LCID]
stormlib.SFileSetLocale.restype = ctypes.wintypes.LCID

# LCID   WINAPI SFileGetLocale()
stormlib.SFileGetLocale.restype = ctypes.wintypes.LCID

# bool   WINAPI SFileOpenArchive(const TCHAR * szMpqName, DWORD dwPriority, DWORD dwFlags, HANDLE * phMpq)
stormlib.SFileOpenArchive.argtypes = [
    ctypes.c_wchar_p,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD,
    ctypes.POINTER(ctypes.wintypes.HANDLE),
]
stormlib.SFileOpenArchive.restype = ctypes.c_bool

# bool   WINAPI SFileHasFile(HANDLE hMpq, const char * szFileName)
stormlib.SFileHasFile.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_char_p]
stormlib.SFileHasFile.restype = ctypes.c_bool

# bool WINAPI SFileOpenFileEx(HANDLE hMpq, const char * szFileName, DWORD dwSearchScope, HANDLE * PtrFile)
stormlib.SFileOpenFileEx.argtypes = [
    ctypes.wintypes.HANDLE,
    ctypes.c_char_p,
    ctypes.wintypes.DWORD,
    ctypes.POINTER(ctypes.wintypes.HANDLE),
]
stormlib.SFileOpenFileEx.restype = ctypes.c_bool

# bool   WINAPI SFileCloseFile(HANDLE hFile)
stormlib.SFileCloseFile.argtypes = [ctypes.wintypes.HANDLE]
stormlib.SFileCloseFile.restype = ctypes.c_bool

# DWORD  WINAPI SFileGetFileSize(HANDLE hFile, LPDWORD pdwFileSizeHigh)
stormlib.SFileGetFileSize.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.LPDWORD]
stormlib.SFileGetFileSize.restype = ctypes.wintypes.DWORD

# bool   WINAPI SFileReadFile(HANDLE hFile, void * lpBuffer, DWORD dwToRead, LPDWORD pdwRead, LPOVERLAPPED lpOverlapped)
stormlib.SFileReadFile.argtypes = [
    ctypes.wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.LPDWORD,
    ctypes.c_void_p,
]
stormlib.SFileReadFile.restype = ctypes.c_bool

# DWORD  WINAPI SFileAddListFile(HANDLE hMpq, const TCHAR * szListFile)
stormlib.SFileAddListFile.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_wchar_p]
stormlib.SFileAddListFile.restype = ctypes.wintypes.DWORD

# bool   WINAPI SFileRemoveFile(HANDLE hMpq, const char * szFileName, DWORD dwSearchScope)
stormlib.SFileRemoveFile.argtypes = [
    ctypes.wintypes.HANDLE,
    ctypes.c_char_p,
    ctypes.wintypes.DWORD,
]
stormlib.SFileRemoveFile.restype = ctypes.c_bool

# bool   WINAPI SFileCreateFile(HANDLE hMpq, const char * szArchivedName, ULONGLONG FileTime, DWORD dwFileSize, LCID lcFileLocale, DWORD dwFlags, HANDLE * phFile)
stormlib.SFileCreateFile.argtypes = [
    ctypes.wintypes.HANDLE,
    ctypes.c_char_p,
    ctypes.c_uint64,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.LCID,
    ctypes.wintypes.DWORD,
    ctypes.POINTER(ctypes.wintypes.HANDLE),
]
stormlib.SFileCreateFile.restype = ctypes.c_bool

# bool   WINAPI SFileWriteFile(HANDLE hFile, const void * pvData, DWORD dwSize, DWORD dwCompression)
stormlib.SFileWriteFile.argtypes = [
    ctypes.wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD,
]
stormlib.SFileWriteFile.restype = ctypes.c_bool

# bool   WINAPI SFileFinishFile(HANDLE hFile)
stormlib.SFileFinishFile.argtypes = [ctypes.wintypes.HANDLE]
stormlib.SFileFinishFile.restype = ctypes.c_bool

# bool   WINAPI SFileAddFileEx(HANDLE hMpq, const TCHAR * szFileName, const char * szArchivedName, DWORD dwFlags, DWORD dwCompression, DWORD dwCompressionNext)
stormlib.SFileAddFileEx.argtypes = [
    ctypes.wintypes.HANDLE,
    ctypes.c_wchar_p,
    ctypes.c_char_p,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD,
]
stormlib.SFileAddFileEx.restype = ctypes.c_bool

# HANDLE WINAPI SFileFindFirstFile(HANDLE hMpq, const char * szMask, SFILE_FIND_DATA * lpFindFileData, const TCHAR * szListFile)
stormlib.SFileFindFirstFile.argtypes = [
    ctypes.wintypes.HANDLE,
    ctypes.c_char_p,
    ctypes.POINTER(SFileFindDataStrc),
    ctypes.c_wchar_p,
]
stormlib.SFileFindFirstFile.restype = ctypes.wintypes.HANDLE

# bool   WINAPI SFileFindNextFile(HANDLE hFind, SFILE_FIND_DATA * lpFindFileData)
stormlib.SFileFindNextFile.argtypes = [
    ctypes.wintypes.HANDLE,
    ctypes.POINTER(SFileFindDataStrc),
]
stormlib.SFileFindNextFile.restype = ctypes.c_bool

# bool   WINAPI SFileFindClose(HANDLE hFind)
stormlib.SFileFindClose.argtypes = [ctypes.wintypes.HANDLE]
stormlib.SFileFindClose.restype = ctypes.c_bool

# bool   WINAPI SFileCompactArchive(HANDLE hMpq, const TCHAR * szListFile, bool bReserved)
stormlib.SFileCompactArchive.argtypes = [
    ctypes.wintypes.HANDLE,
    ctypes.c_wchar_p,
    ctypes.c_bool,
]
stormlib.SFileCompactArchive.restype = ctypes.c_bool
