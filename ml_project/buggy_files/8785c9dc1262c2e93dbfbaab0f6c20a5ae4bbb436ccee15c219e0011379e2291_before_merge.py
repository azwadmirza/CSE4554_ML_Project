    def write_file(self, filename, encoding='utf-8'):
        with codecs.open(filename, 'wb', encoding) as fp:
            self.write(fp)