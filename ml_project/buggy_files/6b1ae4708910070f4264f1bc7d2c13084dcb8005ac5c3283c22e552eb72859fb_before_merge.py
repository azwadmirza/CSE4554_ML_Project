    def parse_timerange(text: str) -> Optional[Tuple[List, int, int]]:
        """
        Parse the value of the argument --timerange to determine what is the range desired
        :param text: value from --timerange
        :return: Start and End range period
        """
        if text is None:
            return None
        syntax = [(r'^-(\d{8})$', (None, 'date')),
                  (r'^(\d{8})-$', ('date', None)),
                  (r'^(\d{8})-(\d{8})$', ('date', 'date')),
                  (r'^(-\d+)$', (None, 'line')),
                  (r'^(\d+)-$', ('line', None)),
                  (r'^(\d+)-(\d+)$', ('index', 'index'))]
        for rex, stype in syntax:
            # Apply the regular expression to text
            match = re.match(rex, text)
            if match:  # Regex has matched
                rvals = match.groups()
                index = 0
                start = None
                stop = None
                if stype[0]:
                    start = rvals[index]
                    if stype[0] != 'date':
                        start = int(start)
                    index += 1
                if stype[1]:
                    stop = rvals[index]
                    if stype[1] != 'date':
                        stop = int(stop)
                return stype, start, stop
        raise Exception('Incorrect syntax for timerange "%s"' % text)