    def _load_from_db(self):

        log.debug(u'{id}: Loading show info from database',
                  {'id': self.series_id})

        main_db_con = db.DBConnection()
        sql_results = main_db_con.select(
            'SELECT *'
            ' FROM tv_shows'
            ' WHERE indexer = ?'
            ' AND indexer_id = ?',
            [self.indexer, self.series_id]
        )

        if not sql_results:
            log.info(u'{id}: Unable to find the show in the database',
                     {'id': self.series_id})
            return
        else:
            self.show_id = int(sql_results[0]['show_id'] or 0)
            self.indexer = int(sql_results[0]['indexer'] or 0)

            if not self.name:
                self.name = sql_results[0]['show_name']
            if not self.network:
                self.network = sql_results[0]['network']
            if not self.genre:
                self.genre = sql_results[0]['genre']
            if not self.classification:
                self.classification = sql_results[0]['classification']

            self.runtime = sql_results[0]['runtime']

            self.status = sql_results[0]['status']
            if self.status is None:
                self.status = 'Unknown'

            self.airs = sql_results[0]['airs']
            if self.airs is None or not network_timezones.test_timeformat(self.airs):
                self.airs = ''

            self.start_year = int(sql_results[0]['startyear'] or 0)
            self.air_by_date = int(sql_results[0]['air_by_date'] or 0)
            self.anime = int(sql_results[0]['anime'] or 0)
            self.sports = int(sql_results[0]['sports'] or 0)
            self.scene = int(sql_results[0]['scene'] or 0)
            self.subtitles = int(sql_results[0]['subtitles'] or 0)
            self.notify_list = dict(ast.literal_eval(sql_results[0]['notify_list'] or '{}'))
            self.dvd_order = int(sql_results[0]['dvdorder'] or 0)
            self.quality = int(sql_results[0]['quality'] or Quality.NA)
            self.season_folders = int(not (sql_results[0]['flatten_folders'] or 0))  # TODO: Rename this in the DB
            self.paused = int(sql_results[0]['paused'] or 0)
            self._location = sql_results[0]['location']  # skip location validation

            if not self.lang:
                self.lang = sql_results[0]['lang']

            self.last_update_indexer = sql_results[0]['last_update_indexer']

            self.rls_ignore_words = sql_results[0]['rls_ignore_words']
            self.rls_require_words = sql_results[0]['rls_require_words']
            self.rls_ignore_exclude = sql_results[0]['rls_ignore_exclude']
            self.rls_require_exclude = sql_results[0]['rls_require_exclude']

            self.default_ep_status = int(sql_results[0]['default_ep_status'] or SKIPPED)

            if not self.imdb_id:
                self.imdb_id = sql_results[0]['imdb_id']

            self.release_groups = BlackAndWhiteList(self)

            self.plot = sql_results[0]['plot']

            # Load external id's from indexer_mappings table.
            self.externals = load_externals_from_db(self.indexer, self.series_id)

            self.airdate_offset = int(sql_results[0]['airdate_offset'])

        # Get IMDb_info from database
        main_db_con = db.DBConnection()
        sql_results = main_db_con.select(
            'SELECT * '
            'FROM imdb_info'
            ' WHERE indexer = ?'
            ' AND indexer_id = ?',
            [self.indexer, self.series_id]
        )

        if not sql_results:
            log.info(u'{id}: Unable to find IMDb info in the database: {show}',
                     {'id': self.series_id, 'show': self.name})
            return
        else:
            self.imdb_info = sql_results[0]

        self.reset_dirty()
        return True