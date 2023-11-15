    def check_minions(self,
                      expr,
                      expr_form='glob',
                      delimiter=DEFAULT_TARGET_DELIM,
                      greedy=True):
        '''
        Check the passed regex against the available minions' public keys
        stored for authentication. This should return a set of ids which
        match the regex, this will then be used to parse the returns to
        make sure everyone has checked back in.
        '''
        try:
            check_func = getattr(self, '_check_{0}_minions'.format(expr_form), None)
            if expr_form in ('grain',
                             'grain_pcre',
                             'pillar',
                             'pillar_pcre',
                             'pillar_exact',
                             'compound',
                             'compound_pillar_exact'):
                minions = check_func(expr, delimiter, greedy)
            else:
                minions = check_func(expr, greedy)
        except Exception:
            log.exception(
                    'Failed matching available minions with {0} pattern: {1}'
                    .format(expr_form, expr))
            minions = []
        return minions