    def load_imdb_info(self):
        """Load all required show information from IMDb with ImdbPie."""
        imdb_api = imdbpie.Imdb()

        if not self.imdb_id:
            self.imdb_id = helpers.title_to_imdb(self.name, self.start_year, imdb_api)

            if not self.imdb_id:
                log.info(u"{id}: Not loading show info from IMDb, because we don't know its ID.",
                         {'id': self.indexerid})
                return

        # Make sure we only use the first ID
        self.imdb_id = self.imdb_id.split(',')[0]

        log.debug(u'{id}: Loading show info from IMDb with ID: {imdb_id}',
                  {'id': self.indexerid, 'imdb_id': self.imdb_id})

        imdb_obj = imdb_api.get_title_by_id(self.imdb_id)

        # If the show has no year, IMDb returned something we don't want
        if not imdb_obj or not imdb_obj.year:
            log.debug(u'{id}: IMDb returned none or invalid info for {imdb_id}, skipping update.',
                      {'id': self.indexerid, 'imdb_id': self.imdb_id})
            return

        # Set retrieved IMDb ID as imdb_id for externals
        self.externals['imdb_id'] = self.imdb_id

        self.imdb_info = {
            'imdb_id': imdb_obj.imdb_id,
            'title': imdb_obj.title,
            'year': imdb_obj.year,
            'akas': '',
            'genres': '|'.join(imdb_obj.genres or ''),
            'countries': '',
            'country_codes': '',
            'rating': str(imdb_obj.rating) if imdb_obj.rating else '',
            'votes': imdb_obj.votes or '',
            'runtimes': int(imdb_obj.runtime / 60) if imdb_obj.runtime else '',  # Time is returned in seconds
            'certificates': imdb_obj.certification or '',
            'plot': imdb_obj.plots[0] if imdb_obj.plots else imdb_obj.plot_outline or '',
            'last_update': datetime.date.today().toordinal(),
        }

        tmdb_id = self.externals.get('tmdb_id')
        if tmdb_id:
            # Country codes and countries obtained from TMDB's API. Not IMDb info.
            country_codes = Tmdb().get_show_country_codes(tmdb_id)
            if country_codes:
                countries = (from_country_code_to_name(country) for country in country_codes)
                self.imdb_info['countries'] = '|'.join(filter(None, countries))
                self.imdb_info['country_codes'] = '|'.join(country_codes).lower()

        log.debug(u'{id}: Obtained info from IMDb: {imdb_info}',
                  {'id': self.indexerid, 'imdb_info': self.imdb_info})