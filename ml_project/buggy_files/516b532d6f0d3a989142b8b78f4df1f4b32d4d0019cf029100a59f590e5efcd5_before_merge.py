    def _parse_date(self, date_text):
        date_match = date_regex.search(date_text)
        days_ago_match = days_ago_regex.search(date_text)
        first_word = date_text.split(' ')[0].lower().strip()

        if first_word in ['vandaag', 'vanochtend', 'vanmiddag', 'vanavond']:
            return date.today()
        elif first_word == 'gisteren':
            return date.today() - timedelta(days=1)
        elif first_word == 'eergisteren':
            return date.today() - timedelta(days=2)
        elif first_word == 'kijk':
            return None
        elif date_match:
            day = int(date_match.group(1))
            month = months.index(date_match.group(2)) + 1
            year = date_match.group(3)
            if year is None:
                year = date.today().year
            else:
                year = int(year)
            return date(year, month, day)
        elif days_ago_match:
            days_ago = int(days_ago_match.group(1))
            return date.today() - timedelta(days=days_ago)
        else:
            log.error("Cannot understand date '%s'", date_text)
            return date.today()