    def ask_questions(target, demo=False):
        """Ask some questions about Nikola."""
        def urlhandler(default, toconf):
            answer = ask('Site URL', 'https://example.com/')
            try:
                answer = answer.decode('utf-8')
            except (AttributeError, UnicodeDecodeError):
                pass
            if not answer.startswith(u'http'):
                print("    ERROR: You must specify a protocol (http or https).")
                urlhandler(default, toconf)
                return
            if not answer.endswith('/'):
                print("    The URL does not end in '/' -- adding it.")
                answer += '/'

            dst_url = urlsplit(answer)
            try:
                dst_url.netloc.encode('ascii')
            except (UnicodeEncodeError, UnicodeDecodeError):
                # The IDN contains characters beyond ASCII.  We must convert it
                # to Punycode. (Issue #1644)
                nl = dst_url.netloc.encode('idna')
                answer = urlunsplit((dst_url.scheme,
                                     nl,
                                     dst_url.path,
                                     dst_url.query,
                                     dst_url.fragment))
                print("    Converting to Punycode:", answer)

            SAMPLE_CONF['SITE_URL'] = answer

        def prettyhandler(default, toconf):
            SAMPLE_CONF['PRETTY_URLS'] = ask_yesno('Enable pretty URLs (/page/ instead of /page.html) that don\'t need web server configuration?', default=True)
            SAMPLE_CONF['STRIP_INDEXES'] = SAMPLE_CONF['PRETTY_URLS']

        def lhandler(default, toconf, show_header=True):
            if show_header:
                print("We will now ask you to provide the list of languages you want to use.")
                print("Please list all the desired languages, comma-separated, using ISO 639-1 codes.  The first language will be used as the default.")
                print("Type '?' (a question mark, sans quotes) to list available languages.")
            answer = ask('Language(s) to use', 'en')
            while answer.strip() == '?':
                print('\n# Available languages:')
                try:
                    print(SAMPLE_CONF['_SUPPORTED_LANGUAGES'] + '\n')
                except UnicodeEncodeError:
                    # avoid Unicode characters in supported language names
                    print(unidecode.unidecode(SAMPLE_CONF['_SUPPORTED_LANGUAGES']) + '\n')
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
                messages = load_messages(['base'], tr, default, themes_dirs=['themes'])
                SAMPLE_CONF['NAVIGATION_LINKS'] = format_navigation_links(langs, default, messages, SAMPLE_CONF['STRIP_INDEXES'])
            except nikola.utils.LanguageNotFoundError as e:
                print("    ERROR: the language '{0}' is not supported.".format(e.lang))
                print("    Are you sure you spelled the name correctly?  Names are case-sensitive and need to be reproduced as-is (complete with the country specifier, if any).")
                print("\nType '?' (a question mark, sans quotes) to list available languages.")
                lhandler(default, toconf, show_header=False)

        def tzhandler(default, toconf):
            print("\nPlease choose the correct time zone for your blog. Nikola uses the tz database.")
            print("You can find your time zone here:")
            print("https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")
            print("")
            answered = False
            while not answered:
                try:
                    lz = get_localzone()
                except Exception:
                    lz = None
                answer = ask('Time zone', lz if lz else "UTC")
                tz = dateutil.tz.gettz(answer)

                if tz is None:
                    print("    WARNING: Time zone not found.  Searching list of time zones for a match.")
                    all_zones = dateutil.zoneinfo.get_zonefile_instance().zones
                    matching_zones = [zone for zone in all_zones if answer.lower() in zone.lower()]
                    if len(matching_zones) == 1:
                        tz = dateutil.tz.gettz(matching_zones[0])
                        answer = matching_zones[0]
                        print("    Picking '{0}'.".format(answer))
                    elif len(matching_zones) > 1:
                        print("    The following time zones match your query:")
                        print('        ' + '\n        '.join(matching_zones))
                        continue

                if tz is not None:
                    time = datetime.datetime.now(tz).strftime('%H:%M:%S')
                    print("    Current time in {0}: {1}".format(answer, time))
                    answered = ask_yesno("Use this time zone?", True)
                else:
                    print("    ERROR: No matches found.  Please try again.")

            SAMPLE_CONF['TIMEZONE'] = answer

        def chandler(default, toconf):
            print("You can configure comments now.  Type '?' (a question mark, sans quotes) to list available comment systems.  If you do not want any comments, just leave the field blank.")
            answer = ask('Comment system', '')
            while answer.strip() == '?':
                print('\n# Available comment systems:')
                print(SAMPLE_CONF['_SUPPORTED_COMMENT_SYSTEMS'])
                print('')
                answer = ask('Comment system', '')

            while answer and answer not in LEGAL_VALUES['COMMENT_SYSTEM']:
                if answer != '?':
                    print('    ERROR: Nikola does not know this comment system.')
                print('\n# Available comment systems:')
                print(SAMPLE_CONF['_SUPPORTED_COMMENT_SYSTEMS'])
                print('')
                answer = ask('Comment system', '')

            SAMPLE_CONF['COMMENT_SYSTEM'] = answer
            SAMPLE_CONF['COMMENT_SYSTEM_ID'] = ''

            if answer:
                print("You need to provide the site identifier for your comment system.  Consult the Nikola manual for details on what the value should be.  (you can leave it empty and come back later)")
                answer = ask('Comment system site identifier', '')
                SAMPLE_CONF['COMMENT_SYSTEM_ID'] = answer

        STORAGE = {'target': target}

        questions = [
            ('Questions about the site', None, None, None),
            # query, default, toconf, destination
            ('Destination', None, False, '!target'),
            ('Site title', 'My Nikola Site', True, 'BLOG_TITLE'),
            ('Site author', 'Nikola Tesla', True, 'BLOG_AUTHOR'),
            ('Site author\'s e-mail', 'n.tesla@example.com', True, 'BLOG_EMAIL'),
            ('Site description', 'This is a demo site for Nikola.', True, 'BLOG_DESCRIPTION'),
            (urlhandler, None, True, True),
            (prettyhandler, None, True, True),
            ('Questions about languages and locales', None, None, None),
            (lhandler, None, True, True),
            (tzhandler, None, True, True),
            ('Questions about comments', None, None, None),
            (chandler, None, True, True),
        ]

        print("Creating Nikola Site")
        print("====================\n")
        print("This is Nikola v{0}.  We will now ask you a few easy questions about your new site.".format(nikola.__version__))
        print("If you do not want to answer and want to go with the defaults instead, simply restart with the `-q` parameter.")

        for query, default, toconf, destination in questions:
            if target and destination == '!target' and test_destination(target, demo):
                # Skip the destination question if we know it already
                pass
            else:
                if default is toconf is destination is None:
                    print('--- {0} ---'.format(query))
                elif destination is True:
                    query(default, toconf)
                else:
                    answer = ask(query, default)
                    try:
                        answer = answer.decode('utf-8')
                    except (AttributeError, UnicodeDecodeError):
                        pass
                    if toconf:
                        SAMPLE_CONF[destination] = answer
                    if destination == '!target':
                        while not answer or not test_destination(answer, demo):
                            if not answer:
                                print('    ERROR: you need to specify a target directory.\n')
                            answer = ask(query, default)
                        STORAGE['target'] = answer

        print("\nThat's it, Nikola is now configured.  Make sure to edit conf.py to your liking.")
        print("If you are looking for themes and addons, check out https://themes.getnikola.com/ and https://plugins.getnikola.com/.")
        print("Have fun!")
        return STORAGE