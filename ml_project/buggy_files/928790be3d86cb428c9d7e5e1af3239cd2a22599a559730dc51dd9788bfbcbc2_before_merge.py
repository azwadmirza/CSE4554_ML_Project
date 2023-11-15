    def target(self, lang):
        '''
        Returns target index for given language.
        '''
        if not lang in self._target:
            try:
                self._target[lang] = open_dir(
                    settings.WHOOSH_INDEX,
                    indexname='target-%s' % lang
                )
            except whoosh.index.EmptyIndexError:
                self._target[lang] = create_target_index(lang)
        return self._target[lang]