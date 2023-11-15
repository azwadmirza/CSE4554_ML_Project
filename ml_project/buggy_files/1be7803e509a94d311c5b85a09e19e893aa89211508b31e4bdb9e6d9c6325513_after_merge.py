    def _guessit_options(options):
        settings = {
            'name_only': True,
            'allowed_languages': ['en', 'fr'],
            'allowed_countries': ['us', 'uk', 'gb'],
            'single_value': True
        }
        options['episode_prefer_number'] = not options.get('identified_by') == 'ep'
        if options.get('allow_groups'):
            options['expected_group'] = options['allow_groups']
        if 'date_yearfirst' in options:
            options['date_year_first'] = options['date_yearfirst']
        if 'date_dayfirst' in options:
            options['date_day_first'] = options['date_dayfirst']
        else:
            # See https://github.com/guessit-io/guessit/issues/329
            # https://github.com/guessit-io/guessit/pull/333
            # They made changes that break backward compatibility, so we have to make do this hackery
            if options.get('date_year_first'):
                options['date_day_first'] = True
        settings.update(options)
        return settings