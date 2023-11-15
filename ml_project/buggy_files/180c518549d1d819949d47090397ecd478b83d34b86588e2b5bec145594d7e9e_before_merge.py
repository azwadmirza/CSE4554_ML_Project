    def _from_table_row(cls, tr: bs4.Tag) -> 'AtCoderProblem':
        tds = tr.find_all('td')
        assert len(tds) == 5
        path = tds[1].find('a')['href']
        self = cls.from_url('https://atcoder.jp' + path)
        assert self is not None
        self._alphabet = tds[0].text
        self._task_name = tds[1].text
        self._time_limit_msec = int(float(utils.remove_suffix(tds[2].text, ' sec')) * 1000)
        self._memory_limit_byte = int(utils.remove_suffix(tds[3].text, ' MB')) * 1000 * 1000  # TODO: confirm this is MB truly, not MiB
        assert tds[4].text.strip() in ('', 'Submit')
        return self