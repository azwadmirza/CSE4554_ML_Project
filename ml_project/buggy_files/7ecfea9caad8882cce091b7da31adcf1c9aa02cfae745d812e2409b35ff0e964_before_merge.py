    def list_entries(config, test_mode=None):
        log.verbose('Connecting to CouchPotato to retrieve movie list.')
        active_movies_url = CouchPotatoBase.build_url(config.get('base_url'), 'active', config.get('port'),
                                                      config.get('api_key'))
        active_movies_json = CouchPotatoBase.get_json(active_movies_url)
        # Gets profile and quality lists if include_data is TRUE
        if config.get('include_data'):
            log.verbose('Connecting to CouchPotato to retrieve profile data.')
            profile_url = CouchPotatoBase.build_url(config.get('base_url'), 'profiles', config.get('port'),
                                                    config.get('api_key'))
            profile_json = CouchPotatoBase.get_json(profile_url)

        entries = []
        for movie in active_movies_json['movies']:
            quality_req = ''
            log.debug('movie data: {}'.format(movie))
            if movie['status'] == 'active':
                if config.get('include_data') and profile_json:
                    for profile in profile_json['list']:
                        if profile['_id'] == movie['profile_id']:  # Matches movie profile with profile JSON
                            quality_req = CouchPotatoBase.quality_requirement_builder(profile)
                entry = Entry(title=movie["title"],
                              url='',
                              imdb_id=movie['info'].get('imdb'),
                              tmdb_id=movie['info'].get('tmdb_id'),
                              quality_req=quality_req,
                              couchpotato_id=movie.get('_id'))
                if entry.isvalid():
                    log.debug('returning entry %s', entry)
                    entries.append(entry)
                else:
                    log.error('Invalid entry created? %s', entry)
                    continue
                # Test mode logging
                if entry and test_mode:
                    log.info("Test mode. Entry includes:")
                    for key, value in entry.items():
                        log.info('     %s: %s', key.capitalize(), value)

        return entries