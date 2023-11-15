    def __init__(self, zipfile, entry=''):
        """
        Create a new path pointer pointing at the specified entry
        in the given zipfile.

        :raise IOError: If the given zipfile does not exist, or if it
        does not contain the specified entry.
        """
        if isinstance(zipfile, string_types):
            zipfile = OpenOnDemandZipFile(os.path.abspath(zipfile))

        # Normalize the entry string, it should be relative:
        entry = normalize_resource_name(entry, True, '/').lstrip('/')

        # Check that the entry exists:
        if entry:
            try:
                zipfile.getinfo(entry)
            except Exception:
                # Sometimes directories aren't explicitly listed in
                # the zip file.  So if `entry` is a directory name,
                # then check if the zipfile contains any files that
                # are under the given directory.
                if (entry.endswith('/') and
                        [n for n in zipfile.namelist() if n.startswith(entry)]):
                    pass  # zipfile contains a file in that directory.
                else:
                    # Otherwise, complain.
                    raise IOError('Zipfile %r does not contain %r' %
                                  (zipfile.filename, entry))
        self._zipfile = zipfile
        self._entry = entry