    def __init__(self, tokens, settings):
        self.settings = settings
        self.tokens = list(tokens)
        self.filtered_tokens = [t for t in self.tokens if t[1] <= 1]

        self.unset_tokens = []

        self.day = None
        self.month = None
        self.year = None
        self.time = None

        self.auto_order = []

        self._token_day = None
        self._token_month = None
        self._token_year = None
        self._token_time = None

        self.ordered_num_directives = OrderedDict(
            (k, self.num_directives[k])
            for k in (resolve_date_order(settings.DATE_ORDER, lst=True))
        )

        skip_index = []
        skip_component = None
        for index, token_type in enumerate(self.filtered_tokens):

            if index in skip_index:
                continue

            token, type = token_type

            if token in settings.SKIP_TOKENS_PARSER:
                continue

            if self.time is None:
                try:
                    microsecond = MICROSECOND.search(self.filtered_tokens[index+1][0]).group()
                    _is_after_time_token = token.index(":")
                    _is_after_period = self.tokens[
                        self.tokens.index((token, 0)) + 1][0].index('.')
                except:
                    microsecond = None

                if microsecond:
                    mindex = index + 2
                else:
                    mindex = index + 1

                try:
                    meridian = MERIDIAN.search(self.filtered_tokens[mindex][0]).group()
                except:
                    meridian = None

                if any([':' in token, meridian, microsecond]):
                    if meridian and not microsecond:
                        self._token_time = '%s %s' % (token, meridian)
                        skip_index.append(mindex)
                    elif microsecond and not meridian:
                        self._token_time = '%s.%s' % (token, microsecond)
                        skip_index.append(index + 1)
                    elif meridian and microsecond:
                        self._token_time = '%s.%s %s' % (token, microsecond, meridian)
                        skip_index.append(index + 1)
                        skip_index.append(mindex)
                    else:
                        self._token_time = token
                    self.time = lambda: time_parser(self._token_time)
                    continue

            results = self._parse(type, token, settings.FUZZY, skip_component=skip_component)
            for res in results:
                if len(token) == 4 and res[0] == 'year':
                    skip_component = 'year'
                setattr(self, *res)

        known, unknown = get_unresolved_attrs(self)
        params = {}
        for attr in known:
            params.update({attr: getattr(self, attr)})
        for attr in unknown:
            for token, type, _ in self.unset_tokens:
                if type == 0:
                    params.update({attr: int(token)})
                    datetime(**params)
                    setattr(self, '_token_%s' % attr, token)
                    setattr(self, attr, int(token))