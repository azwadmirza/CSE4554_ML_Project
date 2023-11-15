    def dump(self, filename, encoding=None):
        """Dumps the ascii art in the file.

        Args:
            filename (str): File to dump the ascii art.
            encoding (str): Optional. Force encoding, instead of self.encoding.
        """
        with open(filename, mode='w', encoding=encoding or self.encoding) as text_file:
            text_file.write(self.single_string())