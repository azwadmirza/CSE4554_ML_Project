    def _parse_raw_thead(self, table):
        thead = self._parse_thead(table)
        res = []
        if thead:
            res = lmap(self._text_getter, self._parse_th(thead[0]))
        return np.atleast_1d(
            np.array(res).squeeze()) if res and len(res) == 1 else res