    def apply(self, other):
        n = self.n

        wkday, _ = lib.monthrange(other.year, other.month)
        first = _get_firstbday(wkday)

        if other.day > first and n <= 0:
            # as if rolled forward already
            n += 1
        elif other.day < first and n > 0:
            other = other + timedelta(days=first-other.day)
            n -= 1

        other = other + relativedelta(months=n)
        wkday, _ = lib.monthrange(other.year, other.month)
        first = _get_firstbday(wkday)
        result = datetime(other.year, other.month, first)
        return result