    def file_reporter(self, filename):
        # TODO: let coverage.py handle .py files itself
        #ext = os.path.splitext(filename)[1].lower()
        #if ext == '.py':
        #    from coverage.python import PythonFileReporter
        #    return PythonFileReporter(filename)

        filename = canonical_filename(os.path.abspath(filename))
        if self._c_files_map and filename in self._c_files_map:
            c_file, rel_file_path, code = self._c_files_map[filename]
        else:
            c_file, _ = self._find_source_files(filename)
            if not c_file:
                return None  # unknown file
            rel_file_path, code = self._parse_lines(c_file, filename)
            if code is None:
                return None  # no source found
        return CythonModuleReporter(c_file, filename, rel_file_path, code)