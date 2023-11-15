    def _load_details(self, session: Optional[requests.Session] = None, lang: str = 'en'):
        assert lang in ('en', 'ja')
        session = session or utils.get_default_session()
        resp = _request('GET', self.get_url(type='beta', lang=lang), session=session)
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)

        contest_name, _, _ = soup.find('title').text.rpartition(' - ')
        contest_duration = soup.find('small', class_='contest-duration')
        self._start_time, end_time = [self._parse_start_time(a['href']) for a in contest_duration.find_all('a')]
        self._duration = end_time - self._start_time
        if lang == 'en':
            self._contest_name_en = contest_name
        elif lang == 'ja':
            self._contest_name_ja = contest_name
        else:
            assert False
        _, _, self._can_participate = soup.find('span', text=re.compile(r'^(Can Participate|参加対象): ')).text.partition(': ')
        _, _, self._rated_range = soup.find('span', text=re.compile(r'^(Rated Range|Rated対象): ')).text.partition(': ')
        penalty_text = soup.find('span', text=re.compile(r'^(Penalty|ペナルティ): ')).text
        m = re.match(r'(Penalty|ペナルティ): (\d+)( minutes?|分)', penalty_text)
        assert m
        self._penalty = datetime.timedelta(minutes=int(m.group(2)))