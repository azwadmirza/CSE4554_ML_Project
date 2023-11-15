    def _parse_raw_tfoot(self, table):
        tfoot = self._parse_tfoot(table)
        res = []
        if tfoot:
            res = lmap(self._text_getter, self._parse_td(tfoot[0]))
        return np.atleast_1d(
            np.array(res).squeeze()) if res and len(res) == 1 else res