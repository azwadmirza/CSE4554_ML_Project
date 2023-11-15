    def parse_series(self, data, **kwargs):
        log.debug('Parsing series: `%s` [options: %s]', data, kwargs)
        guessit_options = self._guessit_options(kwargs)
        valid = True
        if kwargs.get('name'):
            expected_titles = [kwargs['name']]
            if kwargs.get('alternate_names'):
                expected_titles.extend(kwargs['alternate_names'])
            # apostrophe support
            expected_titles = [title.replace('\'', '(?:\'|\\\'|\\\\\'|-|)?') for title in expected_titles]
            guessit_options['expected_title'] = ['re:' + title for title in expected_titles]
        if kwargs.get('id_regexps'):
            guessit_options['id_regexps'] = kwargs.get('id_regexps')
        start = preferred_clock()
        # If no series name is provided, we don't tell guessit what kind of match we are looking for
        # This prevents guessit from determining that too general of matches are series
        parse_type = 'episode' if kwargs.get('name') else None
        if parse_type:
            guessit_options['type'] = parse_type

        # NOTE: Guessit expects str on PY3 and unicode on PY2 hence the use of future.utils.native
        try:
            guess_result = guessit_api.guessit(native(data), options=guessit_options)
        except GuessitException:
            log.warning('Parsing %s with guessit failed. Most likely a unicode error.', data)
            guess_result = {}

        if guess_result.get('type') != 'episode':
            valid = False

        name = kwargs.get('name')
        country = guess_result.get('country')
        if not name:
            name = guess_result.get('title')
            if not name:
                valid = False
            elif country and hasattr(country, 'alpha2'):
                name += ' (%s)' % country.alpha2
        elif guess_result.matches['title']:
            # Make sure the name match is up to FlexGet standards
            # Check there is no unmatched cruft before the matched name
            title_start = guess_result.matches['title'][0].start
            title_end = guess_result.matches['title'][0].end
            if title_start != 0:
                try:
                    pre_title = max((match[0].end for match in guess_result.matches.values() if
                                     match[0].end <= title_start))
                except ValueError:
                    pre_title = 0
                for char in reversed(data[pre_title:title_start]):
                    if char.isalnum() or char.isdigit():
                        return SeriesParseResult(data=data, valid=False)
                    if char.isspace() or char in '._':
                        continue
                    else:
                        break
            # Check the name doesn't end mid-word (guessit might put the border before or after the space after title)
            if data[title_end - 1].isalnum() and len(data) <= title_end or \
                    not self._is_valid_name(data, guessit_options=guessit_options):
                valid = False
            # If we are in exact mode, make sure there is nothing after the title
            if kwargs.get('strict_name'):
                post_title = sys.maxsize
                for match_type, matches in guess_result.matches.items():
                    if match_type in ['season', 'episode', 'date', 'regexpId']:
                        if matches[0].start < title_end:
                            continue
                        post_title = min(post_title, matches[0].start)
                        if matches[0].parent:
                            post_title = min(post_title, matches[0].parent.start)
                for char in data[title_end:post_title]:
                    if char.isalnum() or char.isdigit():
                        valid = False
        else:
            valid = False
        season = guess_result.get('season')
        episode = guess_result.get('episode')
        if episode is None and 'part' in guess_result:
            episode = guess_result['part']
        if isinstance(episode, list):
            # guessit >=2.1.4 returns a list for multi-packs, but we just want the first one and the number of eps
            episode = episode[0]
        date = guess_result.get('date')
        quality = self._quality(guess_result)
        proper_count = self._proper_count(guess_result)
        group = guess_result.get('release_group')
        # Validate group with from_group
        if not self._is_valid_groups(group, guessit_options.get('allow_groups', [])):
            valid = False
        # Validate country, TODO: LEGACY
        if country and name.endswith(')'):
            p_start = name.rfind('(')
            if p_start != -1:
                parenthetical = re.escape(name[p_start + 1:-1])
                if parenthetical and parenthetical.lower() != str(country).lower():
                    valid = False
        special = guess_result.get('episode_details', '').lower() == 'special'
        if 'episode' not in guess_result.values_list:
            episodes = len(guess_result.values_list.get('part', []))
        else:
            episodes = len(guess_result.values_list['episode'])
        if episodes > 3:
            valid = False
        identified_by = kwargs.get('identified_by', 'auto')
        identifier_type, identifier = None, None
        if identified_by in ['date', 'auto']:
            if date:
                identifier_type = 'date'
                identifier = date
        if not identifier_type and identified_by in ['ep', 'auto']:
            if episode is not None:
                if season is None and kwargs.get('allow_seasonless', True):
                    if 'part' in guess_result:
                        season = 1
                    else:
                        episode_raw = guess_result.matches['episode'][0].initiator.raw
                        if episode_raw and any(c.isalpha() and c.lower() != 'v' for c in episode_raw):
                            season = 1
                if season is not None:
                    identifier_type = 'ep'
                    identifier = (season, episode)

        if not identifier_type and identified_by in ['id', 'auto']:
            if guess_result.matches['regexpId']:
                identifier_type = 'id'
                identifier = '-'.join(match.value for match in guess_result.matches['regexpId'])
        if not identifier_type and identified_by in ['sequence', 'auto']:
            if episode is not None:
                identifier_type = 'sequence'
                identifier = episode
        if (not identifier_type or guessit_options.get('prefer_specials')) and (special or
                                                                        guessit_options.get('assume_special')):
            identifier_type = 'special'
            identifier = guess_result.get('episode_title', 'special')
        if not identifier_type:
            valid = False
        # TODO: Legacy - Complete == invalid
        if 'complete' in normalize_component(guess_result.get('other')):
            valid = False

        parsed = SeriesParseResult(
            data=data,
            name=name,
            episodes=episodes,
            identified_by=identified_by,
            id=identifier,
            id_type=identifier_type,
            quality=quality,
            proper_count=proper_count,
            special=special,
            group=group,
            valid=valid
        )

        log.debug('Parsing result: %s (in %s ms)', parsed, (preferred_clock() - start) * 1000)
        return parsed