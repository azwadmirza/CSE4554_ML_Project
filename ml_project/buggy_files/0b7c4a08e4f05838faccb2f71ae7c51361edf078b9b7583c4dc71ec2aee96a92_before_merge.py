    def source(self):
        '''
        Returns source index.
        '''
        if self._source is None:
            try:
                self._source = open_dir(
                    settings.WHOOSH_INDEX,
                    indexname='source'
                )
            except whoosh.index.EmptyIndexError:
                self._source = create_source_index()
            except IOError:
                # eg. path does not exist
                self._source = create_source_index()
        return self._source