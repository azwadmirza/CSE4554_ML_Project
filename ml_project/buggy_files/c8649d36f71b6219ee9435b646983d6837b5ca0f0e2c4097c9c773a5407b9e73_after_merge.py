    def summary_str(self, title: Optional[str] = None, end='\n') -> str:
        """Make a summary string of all of the factories."""
        rows = self._summary_rows()
        n_triples = sum(count for *_, count in rows)
        rows.append(('Total', '-', '-', n_triples))
        t = tabulate(rows, headers=['Name', 'Entities', 'Relations', 'Triples'])
        return f'{title or self.__class__.__name__} (create_inverse_triples={self.create_inverse_triples})\n{t}{end}'