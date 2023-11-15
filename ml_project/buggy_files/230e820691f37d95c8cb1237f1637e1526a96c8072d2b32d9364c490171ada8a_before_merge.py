    def editShow(self, indexername=None, seriesid=None, location=None, allowed_qualities=None, preferred_qualities=None,
                 exceptions_list=None, flatten_folders=None, paused=None, directCall=False,
                 air_by_date=None, sports=None, dvd_order=None, indexer_lang=None,
                 subtitles=None, rls_ignore_words=None, rls_require_words=None,
                 anime=None, blacklist=None, whitelist=None, scene=None,
                 defaultEpStatus=None, quality_preset=None):
        # @TODO: Replace with PATCH /api/v2/show/{id}

        allowed_qualities = allowed_qualities or []
        preferred_qualities = preferred_qualities or []
        exceptions = exceptions_list or set()

        anidb_failed = False
        errors = 0

        if not indexername or not seriesid:
            error_string = 'No show was selected'
            if directCall:
                errors += 1
                return errors
            else:
                return self._genericMessage('Error', error_string)

        series_obj = Show.find_by_id(app.showList, indexer_name_to_id(indexername), seriesid)

        if not series_obj:
            error_string = 'Unable to find the specified show ID: {show}'.format(show=series_obj)
            if directCall:
                errors += 1
                return errors
            else:
                return self._genericMessage('Error', error_string)

        t = PageTemplate(rh=self, filename='editShow.mako')
        return t.render(show=series_obj, title='Edit Show', header='Edit Show',
                        controller='home', action='editShow')