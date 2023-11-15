    def __init__(self):
        """Gets a list of most popular TV series from imdb"""

        self.base_url = 'https://imdb.com'
        self.url = urljoin(self.base_url, 'search/title')

        self.params = {
            'at': 0,
            'sort': 'moviemeter',
            'title_type': 'tv_series',
            'year': '{0},{1}'.format(date.today().year - 1, date.today().year + 1)
        }

        self.session = helpers.make_session()