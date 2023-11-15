    def search(self, name, language=None, exact=False, indexer_id=False):
        """
        :param name: Show name to search for
        :param language: Language of the show info we want
        :param exact: Exact when adding existing, processed when adding new shows
        :param indexer_id: Exact indexer id to get, either imdb or tvdb id.
        :return: list of series objects
        """
        language = language or self.language
        result = []
        if re.match(r'^t?t?\d{7,8}$', str(name)) or re.match(r'^\d{6}$', name):
            try:
                if re.match(r'^t?t?\d{7,8}$', str(name)):
                    result = self._search(imdbId=f'tt{name.strip("t")}', language=language)
                elif re.match(r'^\d{6}$', str(name)):
                    series = self._series(name, language=language)
                    if series:
                        result = [series.info(language)]
            except HTTPError:
                logger.exception(traceback.format_exc())
        else:
            # Name as provided (usually from nfo)
            names = [name]
            if not exact:
                # Name without year and separator
                test = re.match(r'^(.+?)[. -]+\(\d{4}\)?$', name)
                if test:
                    names.append(test.group(1).strip())
                # Name with spaces
                if re.match(r'[. -_]', name):
                    names.append(re.sub(r'[. -_]', ' ', name).strip())
                    if test:
                        # Name with spaces and without year
                        names.append(re.sub(r'[. -_]', ' ', test.group(1)).strip())

            for attempt in set(n for n in names if n.strip()):
                try:
                    result = self._search(attempt, language=language)
                    if result:
                        break
                except HTTPError:
                    logger.exception(traceback.format_exc())

        return result