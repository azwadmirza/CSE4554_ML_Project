    def format_period(self, char):
        period = {0: 'am', 1: 'pm'}[int(self.value.hour >= 12)]
        for width in ('wide', 'narrow', 'abbreviated'):
            period_names = get_period_names(context='format', width=width, locale=self.locale)
            if period in period_names:
                return period_names[period]
        raise ValueError('Could not format period %s in %s' % (period, self.locale))