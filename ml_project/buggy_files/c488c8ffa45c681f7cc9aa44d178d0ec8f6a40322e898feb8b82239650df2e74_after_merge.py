    def _get_library(library_file=None):
        os_is_nt = os.name in ("nt", "dos", "os2", "ce")
        if os_is_nt:
            lib_type = WinDLL
        else:
            lib_type = CDLL
        if library_file is None:
            if os_is_nt:
                library_names = ("MediaInfo.dll",)
            elif sys.platform == "darwin":
                library_names = ("libmediainfo.0.dylib", "libmediainfo.dylib")
            else:
                library_names = ("libmediainfo.so.0",)
            script_dir = os.path.dirname(__file__)
            # Look for the library file in the script folder
            for library in library_names:
                lib_path = os.path.join(script_dir, library)
                if os.path.isfile(lib_path):
                    # If we find it, don't try any other filename
                    library_names = (lib_path,)
                    break
        else:
            library_names = (library_file,)
        for i, library in enumerate(library_names, start=1):
            try:
                return lib_type(library)
            except OSError:
                # If we've tried all possible filenames
                if i == len(library_names):
                    raise