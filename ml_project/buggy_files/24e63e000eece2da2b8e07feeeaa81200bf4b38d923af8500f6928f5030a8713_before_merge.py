    def _guessit_options(self, options):
        settings = {'name_only': True, 'allowed_languages': ['en', 'fr'], 'allowed_countries': ['us', 'uk', 'gb']}
        # 'clean_function': clean_value
        options['episode_prefer_number'] = not options.get('identified_by') == 'ep'
        if options.get('allow_groups'):
            options['expected_group'] = options['allow_groups']
        if 'date_yearfirst' in options:
            options['date_year_first'] = options['date_yearfirst']
        if 'date_dayfirst' in options:
            options['date_day_first'] = options['date_dayfirst']
        settings.update(options)
        return settings