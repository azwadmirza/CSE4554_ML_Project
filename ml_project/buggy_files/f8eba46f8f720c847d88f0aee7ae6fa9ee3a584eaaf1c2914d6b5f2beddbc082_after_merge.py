    def __init__(self):
        """Gets a list of most popular TV series from imdb"""
        self.session = helpers.make_session()
        self.imdb = Imdb(session=self.session)