        def lhandler(default, toconf, show_header=True):
            if show_header:
                print("We will now ask you to provide the list of languages you want to use.")
                print("Please list all the desired languages, comma-separated, using ISO 639-1 codes.  The first language will be used as the default.")
                print("Type '?' (a question mark, sans quotes) to list available languages.")
            answer = ask('Language(s) to use', 'en')
            while answer.strip() == '?':
                print('\n# Available languages:')
                print(SAMPLE_CONF['_SUPPORTED_LANGUAGES'] + '\n')
                answer = ask('Language(s) to use', 'en')

            langs = [i.strip().lower().replace('-', '_') for i in answer.split(',')]
            for partial, full in LEGAL_VALUES['_TRANSLATIONS_WITH_COUNTRY_SPECIFIERS'].items():
                if partial in langs:
                    langs[langs.index(partial)] = full
                    print("NOTICE: Assuming '{0}' instead of '{1}'.".format(full, partial))

            default = langs.pop(0)
            SAMPLE_CONF['DEFAULT_LANG'] = default
            # format_default_translations_config() is intelligent enough to
            # return the current value if there are no additional languages.
            SAMPLE_CONF['TRANSLATIONS'] = format_default_translations_config(langs)

            # Get messages for navigation_links.  In order to do this, we need
            # to generate a throwaway TRANSLATIONS dict.
            tr = {default: ''}
            for l in langs:
                tr[l] = './' + l
            # Assuming that base contains all the locales, and that base does
            # not inherit from anywhere.
            try:
                messages = load_messages(['base'], tr, default)
                SAMPLE_CONF['NAVIGATION_LINKS'] = format_navigation_links(langs, default, messages)
            except nikola.utils.LanguageNotFoundError as e:
                print("    ERROR: the language '{0}' is not supported.".format(e.lang))
                print("    Are you sure you spelled the name correctly?  Names are case-sensitive and need to be reproduced as-is (complete with the country specifier, if any).")
                print("\nType '?' (a question mark, sans quotes) to list available languages.")
                lhandler(default, toconf, show_header=False)