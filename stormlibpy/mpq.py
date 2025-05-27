import ctypes
import ctypes.wintypes
import io
import pathlib
import shutil
import tempfile

from ._stormlib import stormlib, MPQFileFlags, SFileFindDataStrc


def _check(result, func_name=""):
    err_map = {10007: "Could not compact file."}
    if not result:
        err = stormlib.GetLastError()
        err_str = err_map.get(err, ctypes.FormatError(err))
        prefix = "" if not func_name else f"{func_name} failed: "
        raise RuntimeError(f"{prefix}{err} -> {err_str}")
    return result


class MPQArchive:
    WAR3X = (
        MPQFileFlags.MPQ_FILE_COMPRESS
        | MPQFileFlags.MPQ_FILE_ENCRYPTED
        | MPQFileFlags.MPQ_FILE_REPLACEEXISTING,
        MPQFileFlags.MPQ_COMPRESSION_ZLIB,
    )

    def __init__(self, archive_path, listfile_names=None):
        self.original_path = pathlib.Path(archive_path)
        self.temp_path = pathlib.Path(
            tempfile.NamedTemporaryFile(
                delete=False, suffix=self.original_path.suffix
            ).name
        )
        shutil.copy2(self.original_path, self.temp_path)

        self.listfile_names = listfile_names
        self.listfile_path = pathlib.Path(
            tempfile.NamedTemporaryFile(delete=False).name
        )
        self.listfile_path.write_text("\n".join(listfile_names))

        self.hMpq = ctypes.c_void_p()
        self._saved = False

    def __enter__(self):
        _check(
            stormlib.SFileOpenArchive(
                str(self.temp_path), 0, 0, ctypes.byref(self.hMpq)
            ),
            "SFileOpenArchive",
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _close_archive(self):
        if self.hMpq:
            stormlib.SFileCloseArchive(self.hMpq)
            self.hMpq = None

    def close(self):
        self._close_archive()
        if self.temp_path.exists():
            self.temp_path.unlink()
        if self.listfile_path.exists():
            self.listfile_path.unlink()

    def save(self):
        self._close_archive()
        shutil.copy2(self.temp_path, self.original_path)
        self._saved = True

    def compact(self):
        _check(stormlib.SFileCompactArchive(self.hMpq, None, False))

    def list_files(self):
        archive_files = []
        filename = ctypes.c_char_p(bytes("(listfile)", "utf-8"))
        has_listfile = stormlib.SFileHasFile(self.hMpq, filename)
        if has_listfile:
            archive_files = self.read_file("(listfile)").decode("utf-8").splitlines()

        find_file_strc = SFileFindDataStrc()
        extra_listfile = str(self.listfile_path)

        found_files = []
        hFind = stormlib.SFileFindFirstFile(
            self.hMpq, b"*", ctypes.byref(find_file_strc), extra_listfile
        )
        while stormlib.GetLastError() != 18:  # EOF Error
            found_files.append(
                {
                    field: getattr(find_file_strc, field)
                    for field, _ in find_file_strc._fields_
                }
            )
            while stormlib.SFileFindNextFile(hFind, ctypes.byref(find_file_strc)):
                found_files.append(
                    {
                        field: getattr(find_file_strc, field)
                        for field, _ in find_file_strc._fields_
                    }
                )

        archive_files += [f["cFileName"].decode("utf-8") for f in found_files]
        return archive_files

    def read_file(self, filename):
        hFile = ctypes.c_void_p()
        filename = ctypes.c_char_p(bytes(filename, "utf-8"))
        _check(stormlib.SFileOpenFileEx(self.hMpq, filename, 0, ctypes.byref(hFile)))
        dwFileSize = _check(stormlib.SFileGetFileSize(hFile, None))
        if dwFileSize == 0xFFFFFFFF:
            last_error = stormlib.GetLastError()
            raise RuntimeError(
                f"Error: {last_error} -> {ctypes.FormatError(last_error)}"
            )

        bio = io.BytesIO()
        buf = (ctypes.c_ubyte * dwFileSize)()
        bytes_read = ctypes.wintypes.DWORD(1)
        bytes_requested = dwFileSize
        while bytes_read.value:
            if _check(
                stormlib.SFileReadFile(
                    hFile,
                    ctypes.byref(buf),
                    bytes_requested,
                    ctypes.byref(bytes_read),
                    None,
                )
            ):
                bytes_requested -= bytes_read.value
                data = bytes(buf[: bytes_read.value])
                bio.write(data)

        stormlib.SFileCloseFile(hFile)
        bio.seek(0)
        return bio.read()

    def add_file(
        self,
        filepath,
        archived_name=None,
        flag_options=WAR3X,
        compression_next=MPQFileFlags.MPQ_COMPRESSION_NEXT_SAME,
    ):
        file_flags, compression_flags = flag_options
        archived_name = filepath.name if archived_name is None else archived_name
        _check(
            stormlib.SFileAddFileEx(
                self.hMpq,
                str(filepath),
                bytes(archived_name, "utf-8"),
                file_flags,
                compression_flags,
                compression_next,
            )
        )

    def write_file(self, filename, data, overwrite=True, flag_options=WAR3X):
        file_flags, compression_flags = flag_options
        if not overwrite:
            file_flags &= ~MPQFileFlags.MPQ_FILE_REPLACEEXISTING

        pData = ctypes.c_char_p(data)
        hFile = ctypes.c_void_p()

        filename = ctypes.c_char_p(bytes(filename, "utf-8"))

        if stormlib.SFileHasFile(self.hMpq, filename):
            _check(stormlib.SFileRemoveFile(self.hMpq, filename, 0))

        _check(
            stormlib.SFileCreateFile(
                self.hMpq, filename, 0, len(data), 0, compression_flags, hFile
            )
        )
        _check(
            stormlib.SFileWriteFile(
                hFile, pData, len(data), MPQFileFlags.MPQ_COMPRESSION_ZLIB
            )
        )
        _check(stormlib.SFileCloseFile(hFile))

    def remove_file(self, filename):
        filename = ctypes.c_char_p(bytes(filename, "utf-8"))
        _check(stormlib.SFileRemoveFile(self.hMpq, filename, 0))
