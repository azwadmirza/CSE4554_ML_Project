    def write_file(self, filename=None, encoding='utf-8'):
        if not filename:
            filename = self.filename

        with codecs.open(filename, 'wb', encoding) as fp:
            self.write(fp)