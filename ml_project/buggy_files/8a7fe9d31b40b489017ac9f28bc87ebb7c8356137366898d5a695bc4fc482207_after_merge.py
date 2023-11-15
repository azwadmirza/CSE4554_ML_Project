    def fetch_popular_shows(self):
        """Get popular show information from IMDB"""
        return self.imdb.get_popular_shows()