        def scan(i, token, column):
            to_scan = column.to_scan.get_news()

            for x in self.ignore:
                m = x.match(stream, i)
                if m:
                    # TODO add partial matches for ignore too?
                    delayed_matches[m.end()] += to_scan

            for item in to_scan:
                m = item.expect.match(stream, i)
                if m:
                    t = Token(item.expect.name, m.group(0), i, text_line, text_column)
                    delayed_matches[m.end()].append(item.advance(t))

                    s = m.group(0)
                    for j in range(1, len(s)):
                        m = item.expect.match(s[:-j])
                        if m:
                            delayed_matches[m.end()].append(item.advance(m.group(0)))

            next_set = Column(i+1)
            next_set.add(delayed_matches[i+1])
            del delayed_matches[i+1]    # No longer needed, so unburden memory

            return next_set