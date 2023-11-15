    def __init__(self, name=None, alternate_names=None, identified_by='auto', name_regexps=None, ep_regexps=None,
                 date_regexps=None, sequence_regexps=None, id_regexps=None, strict_name=False, allow_groups=None,
                 allow_seasonless=True, date_dayfirst=None, date_yearfirst=None, special_ids=None,
                 prefer_specials=False, assume_special=False):
        """
        Init SeriesParser.

        :param string name: Name of the series parser is going to try to parse. If not supplied series name will be
            guessed from data.
        :param list alternate_names: Other names for this series that should be allowed.
        :param string identified_by: What kind of episode numbering scheme is expected,
            valid values are ep, date, sequence, id and auto (default).
        :param list name_regexps: Regexps for name matching or None (default),
            by default regexp is generated from name.
        :param list ep_regexps: Regexps detecting episode,season format.
            Given list is prioritized over built-in regexps.
        :param list date_regexps: Regexps detecting date format.
            Given list is prioritized over built-in regexps.
        :param list sequence_regexps: Regexps detecting sequence format.
            Given list is prioritized over built-in regexps.
        :param list id_regexps: Custom regexps detecting id format.
            Given list is prioritized over built in regexps.
        :param boolean strict_name: If True name must be immediately be followed by episode identifier.
        :param list allow_groups: Optionally specify list of release group names that are allowed.
        :param date_dayfirst: Prefer day first notation of dates when there are multiple possible interpretations.
        :param date_yearfirst: Prefer year first notation of dates when there are multiple possible interpretations.
            This will also populate attribute `group`.
        :param special_ids: Identifiers which will cause entry to be flagged as a special.
        :param boolean prefer_specials: If True, label entry which matches both a series identifier and a special
            identifier as a special.
        """

        self.episodes = 1
        self.name = name
        self.alternate_names = alternate_names or []
        self.data = ''
        self.identified_by = identified_by
        # Stores the type of identifier found, 'ep', 'date', 'sequence' or 'special'
        self.id_type = None
        self.name_regexps = ReList(name_regexps or [])
        self.re_from_name = False
        # If custom identifier regexps were provided, prepend them to the appropriate type of built in regexps
        for mode in ID_TYPES:
            listname = mode + '_regexps'
            if locals()[listname]:
                setattr(self, listname, ReList(locals()[listname] + getattr(SeriesParser, listname)))
        self.specials = self.specials + [i.lower() for i in (special_ids or [])]
        self.prefer_specials = prefer_specials
        self.assume_special = assume_special
        self.strict_name = strict_name
        self.allow_groups = allow_groups or []
        self.allow_seasonless = allow_seasonless
        self.date_dayfirst = date_dayfirst
        self.date_yearfirst = date_yearfirst

        self.field = None
        self._reset()