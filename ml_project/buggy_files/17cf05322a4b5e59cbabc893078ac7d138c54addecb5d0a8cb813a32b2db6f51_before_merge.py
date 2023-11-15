    def read_file(self, filename, encoding='utf-8'):
        with codecs.open(filename, 'rb', encoding) as fp:
            self.readfp(fp)