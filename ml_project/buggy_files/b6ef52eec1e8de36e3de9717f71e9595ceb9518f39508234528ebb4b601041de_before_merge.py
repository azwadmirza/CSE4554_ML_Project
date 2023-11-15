    def popularShows(self):
        """
        Fetches data from IMDB to show a list of popular shows.
        """
        t = PageTemplate(rh=self, filename="addShows_popularShows.mako")
        e = None

        try:
            popular_shows = imdb_popular.fetch_popular_shows()
        except Exception as e:
            logger.warning("Could not get popular shows: {0}".format(str(e)))
            popular_shows = None

        return t.render(title=_("Popular Shows"), header=_("Popular Shows"),
                        popular_shows=popular_shows, imdb_exception=e,
                        topmenu="home",
                        controller="addShows", action="popularShows")