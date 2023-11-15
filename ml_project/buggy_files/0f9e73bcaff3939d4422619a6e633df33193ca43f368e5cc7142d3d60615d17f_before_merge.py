    def _get_writer(self, outpath):
        return file_writer(outpath, newline=self._options['line_separator'])