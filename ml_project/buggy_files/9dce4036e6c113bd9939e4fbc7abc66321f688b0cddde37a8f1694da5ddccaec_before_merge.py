    def patch(self, series_slug, path_param=None):
        """Patch series."""
        if not series_slug:
            return self._method_not_allowed('Patching multiple series is not allowed')

        identifier = SeriesIdentifier.from_slug(series_slug)
        if not identifier:
            return self._bad_request('Invalid series identifier')

        series = Series.find_by_identifier(identifier)
        if not series:
            return self._not_found('Series not found')

        data = json_decode(self.request.body)
        indexer_id = data.get('id', {}).get(identifier.indexer.slug)
        if indexer_id is not None and indexer_id != identifier.id:
            return self._bad_request('Conflicting series identifier')

        accepted = {}
        ignored = {}
        patches = {
            'config.aliases': ListField(series, 'aliases'),
            'config.dvdOrder': BooleanField(series, 'dvd_order'),
            'config.flattenFolders': BooleanField(series, 'flatten_folders'),
            'config.anime': BooleanField(series, 'anime'),
            'config.scene': BooleanField(series, 'scene'),
            'config.sports': BooleanField(series, 'sports'),
            'config.paused': BooleanField(series, 'paused'),
            'config.location': StringField(series, '_location'),
            'config.airByDate': BooleanField(series, 'air_by_date'),
            'config.subtitlesEnabled': BooleanField(series, 'subtitles'),
            'config.release.requiredWords': ListField(series, 'release_required_words'),
            'config.release.ignoredWords': ListField(series, 'release_ignore_words'),
            'config.release.blacklist': ListField(series, 'blacklist'),
            'config.release.whitelist': ListField(series, 'whitelist'),
            'language': StringField(series, 'lang'),
            'config.qualities.allowed': ListField(series, 'qualities_allowed'),
            'config.qualities.preferred': ListField(series, 'qualities_preferred'),
            'config.qualities.combined': IntegerField(series, 'quality'),
        }
        for key, value in iter_nested_items(data):
            patch_field = patches.get(key)
            if patch_field and patch_field.patch(series, value):
                set_nested_value(accepted, key, value)
            else:
                set_nested_value(ignored, key, value)

        # Save patched attributes in db.
        series.save_to_db()

        if ignored:
            log.warning('Series patch ignored %r', ignored)

        self._ok(data=accepted)