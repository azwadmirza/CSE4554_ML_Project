    def parse(self, data=None, field=None, quality=None):
        # Clear the output variables before parsing
        self._reset()
        self.field = field
        if quality:
            self.quality = quality
        if data:
            self.data = data
        if not self.data:
            raise ParseWarning(self, 'No data supplied to parse.')
        if not self.name:
            log.debug('No name for series `%s` supplied, guessing name.', self.data)
            if not self.guess_name():
                log.debug('Could not determine a series name')
                return
            log.debug('Series name for %s guessed to be %s', self.data, self.name)

        # check if data appears to be unwanted (abort)
        if self.parse_unwanted(self.remove_dirt(self.data)):
            raise ParseWarning(self, '`{data}` appears to be an episode pack'.format(data=self.data))

        name = self.remove_dirt(self.name)

        log.debug('name: %s data: %s', name, self.data)

        # name end position
        name_start = 0
        name_end = 0

        # regexp name matching
        if not self.name_regexps:
            # if we don't have name_regexps, generate one from the name
            self.name_regexps = ReList(
                name_to_re(name, self.ignore_prefixes, self) for name in [self.name] + self.alternate_names)
            # With auto regex generation, the first regex group captures the name
            self.re_from_name = True
        # try all specified regexps on this data
        for name_re in self.name_regexps:
            match = re.search(name_re, self.data)
            if match:
                match_start, match_end = match.span(1 if self.re_from_name else 0)
                # Always pick the longest matching regex
                if match_end > name_end:
                    name_start, name_end = match_start, match_end
                log.debug('NAME SUCCESS: %s matched to %s', name_re.pattern, self.data)
        if not name_end:
            # leave this invalid
            log.debug('FAIL: name regexps %s do not match %s',
                      [regexp.pattern for regexp in self.name_regexps], self.data)
            return

        # remove series name from raw data, move any prefix to end of string
        data_stripped = self.data[name_end:] + ' ' + self.data[:name_start]
        data_stripped = data_stripped.lower()
        log.debug('data stripped: %s', data_stripped)

        # allow group(s)
        if self.allow_groups:
            for group in self.allow_groups:
                group = group.lower()
                for fmt in ['[%s]', '-%s', '(%s)']:
                    if fmt % group in data_stripped:
                        log.debug('%s is from group %s', self.data, group)
                        self.group = group
                        data_stripped = data_stripped.replace(fmt % group, '')
                        break
                if self.group:
                    break
            else:
                log.debug('%s is not from groups %s', self.data, self.allow_groups)
                return  # leave invalid

        # Find quality and clean from data
        log.debug('parsing quality ->')
        quality = qualities.Quality(data_stripped)
        if quality:
            # Remove quality string from data
            log.debug('quality detected, using remaining data `%s`', quality.clean_text)
            data_stripped = quality.clean_text
        # Don't override passed in quality
        if not self.quality:
            self.quality = quality

        # Remove unwanted words from data for ep / id parsing
        data_stripped = self.remove_words(data_stripped, self.remove, not_in_word=True)

        data_parts = re.split('[\W_]+', data_stripped)

        for part in data_parts[:]:
            if part in self.propers:
                self.proper_count += 1
                data_parts.remove(part)
            elif part == 'fastsub':
                # Subtract 5 to leave room for fastsub propers before the normal release
                self.proper_count -= 5
                data_parts.remove(part)
            elif part in self.specials:
                self.special = True
                data_parts.remove(part)

        data_stripped = ' '.join(data_parts).strip()

        log.debug("data for date/ep/id parsing '%s'", data_stripped)

        # Try date mode before ep mode
        if self.identified_by in ['date', 'auto']:
            date_match = self.parse_date(data_stripped)
            if date_match:
                if self.strict_name:
                    if date_match['match'].start() > 1:
                        return
                self.id = date_match['date']
                self.id_groups = date_match['match'].groups()
                self.id_type = 'date'
                self.valid = True
                if not (self.special and self.prefer_specials):
                    return
            else:
                log.debug('-> no luck with date_regexps')

        if self.identified_by in ['ep', 'auto'] and not self.valid:
            ep_match = self.parse_episode(data_stripped)
            if ep_match:
                # strict_name
                if self.strict_name:
                    if ep_match['match'].start() > 1:
                        return

                if ep_match['end_episode'] and ep_match['end_episode'] > ep_match['episode'] + 2:
                    # This is a pack of too many episodes, ignore it.
                    log.debug('Series pack contains too many episodes (%d). Rejecting',
                              ep_match['end_episode'] - ep_match['episode'])
                    return

                self.season = ep_match['season']
                self.episode = ep_match['episode']
                if ep_match['end_episode']:
                    self.episodes = (ep_match['end_episode'] - ep_match['episode']) + 1

                self.id = (self.season, self.episode)
                self.id_type = 'ep'
                self.valid = True
                if not (self.special and self.prefer_specials):
                    return
            else:
                season_pack_match = self.parse_season_packs(data_stripped)
                # If a title looks like a special, give it precedence over season pack
                if season_pack_match and not self.special:
                    if self.strict_name and season_pack_match['match'].start() > 1:
                        return
                    self.season = season_pack_match['season']
                    self.season_pack = True
                    self.id = (season_pack_match['season'], 0)
                    self.id_type = 'ep'
                    self.valid = True
                else:
                    log.debug('-> no luck with ep_regexps')

            if self.identified_by == 'ep' and not self.season_pack:
                # we should be getting season, ep !
                # try to look up idiotic numbering scheme 101,102,103,201,202
                # ressu: Added matching for 0101, 0102... It will fail on
                #        season 11 though
                log.debug('ep identifier expected. Attempting SEE format parsing.')
                match = re.search(self.re_not_in_word(r'(\d?\d)(\d\d)'), data_stripped, re.IGNORECASE | re.UNICODE)
                if match:
                    # strict_name
                    if self.strict_name:
                        if match.start() > 1:
                            return

                    self.season = int(match.group(1))
                    self.episode = int(match.group(2))
                    self.id = (self.season, self.episode)
                    log.debug(self)
                    self.id_type = 'ep'
                    self.valid = True
                    return
                else:
                    log.debug('-> no luck with SEE')

        # Check id regexps
        if self.identified_by in ['id', 'auto'] and not self.valid:
            for id_re in self.id_regexps:
                match = re.search(id_re, data_stripped)
                if match:
                    # strict_name
                    if self.strict_name:
                        if match.start() > 1:
                            return
                    found_id = '-'.join(g for g in match.groups() if g)
                    if not found_id:
                        # If match groups were all blank, don't accept this match
                        continue
                    self.id = found_id
                    self.id_type = 'id'
                    self.valid = True
                    log.debug('found id \'%s\' with regexp \'%s\'', self.id, id_re.pattern)
                    if not (self.special and self.prefer_specials):
                        return
                    else:
                        break
            else:
                log.debug('-> no luck with id_regexps')

        # Other modes are done, check for unwanted sequence ids
        if self.parse_unwanted_sequence(data_stripped):
            return

        # Check sequences last as they contain the broadest matches
        if self.identified_by in ['sequence', 'auto'] and not self.valid:
            for sequence_re in self.sequence_regexps:
                match = re.search(sequence_re, data_stripped)
                if match:
                    # strict_name
                    if self.strict_name:
                        if match.start() > 1:
                            return
                    # First matching group is the sequence number
                    try:
                        self.id = int(match.group(1))
                    except ValueError:
                        self.id = self.roman_to_int(match.group(1))
                    self.season = 0
                    self.episode = self.id
                    # If anime style version was found, overwrite the proper count with it
                    if 'version' in match.groupdict():
                        if match.group('version'):
                            self.proper_count = int(match.group('version')) - 1
                    self.id_type = 'sequence'
                    self.valid = True
                    log.debug('found id \'%s\' with regexp \'%s\'', self.id, sequence_re.pattern)
                    if not (self.special and self.prefer_specials):
                        return
                    else:
                        break
            else:
                log.debug('-> no luck with sequence_regexps')

        # No id found, check if this is a special
        if self.special or self.assume_special:
            # Attempt to set id as the title of the special
            self.id = data_stripped or 'special'
            self.id_type = 'special'
            self.valid = True
            log.debug('found special, setting id to \'%s\'', self.id)
            return
        if self.valid:
            return

        msg = 'Title `%s` looks like series `%s` but cannot find ' % (self.data, self.name)
        if self.identified_by == 'auto':
            msg += 'any series numbering.'
        else:
            msg += 'a(n) `%s` style identifier.' % self.identified_by
        raise ParseWarning(self, msg)