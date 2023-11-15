    def check_understood_rrule(rrule):
        """test if we can reproduce `rrule`."""
        keys = set(rrule.keys())
        freq = rrule.get('FREQ', [None])[0]
        unsupported_rrule_parts = {
            'BYSECOND', 'BYMINUTE', 'BYHOUR', 'BYYEARDAY',
            'BYWEEKNO', 'BYMONTH', 'BYSETPOS',
        }
        if keys.intersection(unsupported_rrule_parts):
            return False
        if len(rrule.get('BYMONTHDAY', [1])) > 1:
            return False
        # we don't support negative BYMONTHDAY numbers
        # don't need to check whole list, we only support one monthday anyway
        if rrule.get('BYMONTHDAY', [1])[0] < 1:
            return False
        if rrule.get('BYDAY', ['1'])[0][0] == '-':
            return False
        if freq not in ['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY']:
            return False
        if 'BYDAY' in keys and freq == 'YEARLY':
            return False
        return True