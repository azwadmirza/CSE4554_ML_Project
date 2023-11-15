    def __iter__(self):
        '''Simple iterator to go over all sources. Empty, non-source, and other not valid lines will be skipped.'''
        for file, sources in self.files.items():
            for n, valid, enabled, source, comment in sources:
                if valid:
                    yield file, n, enabled, source, comment
        raise StopIteration