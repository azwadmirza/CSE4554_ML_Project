    def load_imdb_info(self):
        """Load all required show information from IMDb with IMDbPY."""
        imdb_api = imdb.IMDb()

        try:
            if not self.imdbid:
                self.imdbid = imdb_api.title2imdbID(self.name, kind='tv series')

            if not self.imdbid:
                logger.log(u'{0}: Not loading show info from IMDb, '
                           u"because we don't know its ID".format(self.indexerid))
                return

            # Make sure we only use one ID
            imdb_id = self.imdbid.split(',')[0]

            logger.log(u'{0}: Loading show info from IMDb with ID: {1}'.format(
                       self.indexerid, imdb_id), logger.DEBUG)

            # Remove first two chars from ID
            imdb_obj = imdb_api.get_movie(imdb_id[2:])

        except IMDbDataAccessError:
            logger.log(u'{0}: Failed to obtain info from IMDb for: {1}'.format(
                       self.indexerid, self.name), logger.DEBUG)
            return

        except IMDbParserError:
            logger.log(u'{0}: Failed to parse info from IMDb for: {1}'.format(
                       self.indexerid, self.name), logger.ERROR)
            return

        self.imdb_info = {
            'imdb_id': imdb_id,
            'title': imdb_obj.get('title', ''),
            'year': imdb_obj.get('year', ''),
            'akas': '|'.join(imdb_obj.get('akas', '')),
            'genres': '|'.join(imdb_obj.get('genres', '')),
            'countries': '|'.join(imdb_obj.get('countries', '')),
            'country_codes': '|'.join(imdb_obj.get('country codes', '')),
            'rating': imdb_obj.get('rating', ''),
            'votes': imdb_obj.get('votes', ''),
            'last_update': datetime.date.today().toordinal()
        }

        if imdb_obj.get('runtimes'):
            self.imdb_info['runtimes'] = re.search(r'\d+', imdb_obj['runtimes'][0]).group(0)

        # Get only the production country certificate if any
        if imdb_obj.get('certificates') and imdb_obj.get('countries'):
            for certificate in imdb_obj['certificates']:
                if certificate.split(':')[0] in imdb_obj['countries']:
                    self.imdb_info['certificates'] = certificate.split(':')[1]
                    break

        logger.log(u'{0}: Obtained info from IMDb: {1}'.format(
                   self.indexerid, self.imdb_info), logger.DEBUG)