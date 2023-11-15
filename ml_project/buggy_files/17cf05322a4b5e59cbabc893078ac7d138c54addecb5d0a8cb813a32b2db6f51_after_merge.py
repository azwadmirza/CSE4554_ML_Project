    def read_file(self, filename, encoding='utf-8'):
        self.filename = filename
        with codecs.open(filename, 'rb', encoding) as fp:
            self.readfp(fp)