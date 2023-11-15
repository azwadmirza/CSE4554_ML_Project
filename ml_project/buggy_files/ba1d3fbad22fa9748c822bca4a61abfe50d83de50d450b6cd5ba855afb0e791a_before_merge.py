    def save_to_db(self):
        """Save to database."""
        if not self.dirty:
            return

        log.debug(u'{id}: Saving to database: {show}',
                  {'id': self.series_id, 'show': self.name})

        control_value_dict = {'indexer': self.indexer, 'indexer_id': self.series_id}
        new_value_dict = {'show_name': self.name,
                          'location': self.location,  # skip location validation
                          'network': self.network,
                          'genre': self.genre,
                          'classification': self.classification,
                          'runtime': self.runtime,
                          'quality': self.quality,
                          'airs': self.airs,
                          'status': self.status,
                          'flatten_folders': not self.season_folders,  # TODO: Remove negation after DB change
                          'paused': self.paused,
                          'air_by_date': self.air_by_date,
                          'anime': self.anime,
                          'scene': self.scene,
                          'sports': self.sports,
                          'subtitles': self.subtitles,
                          'dvdorder': self.dvd_order,
                          'startyear': self.start_year,
                          'lang': self.lang,
                          'imdb_id': self.imdb_id,
                          'last_update_indexer': self.last_update_indexer,
                          'rls_ignore_words': self.rls_ignore_words,
                          'rls_require_words': self.rls_require_words,
                          'default_ep_status': self.default_ep_status,
                          'plot': self.plot,
                          'airdate_offset': self.airdate_offset}

        main_db_con = db.DBConnection()
        main_db_con.upsert('tv_shows', new_value_dict, control_value_dict)

        helpers.update_anime_support()

        if self.imdb_id and self.imdb_info.get('year'):
            control_value_dict = {'indexer': self.indexer, 'indexer_id': self.series_id}
            new_value_dict = self.imdb_info

            main_db_con = db.DBConnection()
            main_db_con.upsert('imdb_info', new_value_dict, control_value_dict)

        self.reset_dirty()