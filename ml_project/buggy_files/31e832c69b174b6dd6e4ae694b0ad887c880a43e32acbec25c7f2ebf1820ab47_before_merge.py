    def __init__(self, key=None, allowed_keywords=[], merge_keywords=True, **kwargs):

        invalid_kws = []
        for kwarg in sorted(kwargs.keys()):
            if allowed_keywords and kwarg not in allowed_keywords:
                if self.skip_invalid:
                    invalid_kws.append(kwarg)
                else:
                    raise OptionError(kwarg, allowed_keywords)

        for invalid_kw in invalid_kws:
            error = OptionError(invalid_kw, allowed_keywords, group_name=key)
            StoreOptions.record_skipped_option(error)
        if invalid_kws and self.warn_on_skip:
            self.warning("Invalid options %s, valid options are: %s"
                         % (repr(invalid_kws), str(allowed_keywords)))

        self.kwargs = {k:v for k,v in kwargs.items() if k not in invalid_kws}
        self._options = self._expand_options(kwargs)
        allowed_keywords = (allowed_keywords if isinstance(allowed_keywords, Keywords)
                            else Keywords(allowed_keywords))
        super(Options, self).__init__(allowed_keywords=allowed_keywords,
                                      merge_keywords=merge_keywords, key=key)