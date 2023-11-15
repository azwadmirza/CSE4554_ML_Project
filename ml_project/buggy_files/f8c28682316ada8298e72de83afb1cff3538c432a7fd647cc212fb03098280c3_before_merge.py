    def items(self):
        if self._items is None:
            r = self.session.get('http://www.imdb.com/list/export?list_id=%s&author_id=%s' %
                                 (self.list_id, self.user_id))
            lines = r.iter_lines()
            # Throw away first line with headers
            next(lines)
            self._items = []
            for row in csv.reader(lines):
                row = [unicode(cell, 'utf-8') for cell in row]
                log.debug('parsing line from csv: %s', ', '.join(row))
                if not len(row) == 16:
                    log.debug('no movie row detected, skipping. %s', ', '.join(row))
                    continue
                entry = Entry({
                    'title': '%s (%s)' % (row[5], row[11]) if row[11] != '????' else '%s' % row[5],
                    'url': row[15],
                    'imdb_id': row[1],
                    'imdb_url': row[15],
                    'imdb_list_position': int(row[0]),
                    'imdb_list_created': datetime.strptime(row[2], '%a %b %d %H:%M:%S %Y') if row[2] else None,
                    'imdb_list_modified': datetime.strptime(row[3], '%a %b %d %H:%M:%S %Y') if row[3] else None,
                    'imdb_list_description': row[4],
                    'imdb_name': row[5],
                    'movie_name': row[5],
                    'imdb_year': int(row[11]) if row[11] != '????' else None,
                    'movie_year': int(row[11]) if row[11] != '????' else None,
                    'imdb_score': float(row[9]) if row[9] else None,
                    'imdb_user_score': float(row[8]) if row[8] else None,
                    'imdb_votes': int(row[13]) if row[13] else None,
                    'imdb_genres': [genre.strip() for genre in row[12].split(',')]
                })
                self._items.append(entry)
        return self._items