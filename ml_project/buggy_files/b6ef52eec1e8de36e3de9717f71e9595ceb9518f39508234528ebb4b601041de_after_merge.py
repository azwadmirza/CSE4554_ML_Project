    def popularShows(self):
        """
        Fetches data from IMDB to show a list of popular shows.
        """
        t = PageTemplate(rh=self, filename="addShows_popularShows.mako")
        try:
            popular_shows = imdb_popular.fetch_popular_shows()
            imdb_exception = None
        except Exception as error:
            logger.warning("Could not get popular shows: {0}".format(str(error)))
            logger.debug(traceback.format_exc())
            popular_shows = None
            imdb_exception = error

        return t.render(title=_("Popular Shows"), header=_("Popular Shows"),
                        popular_shows=popular_shows, imdb_exception=imdb_exception,
                        topmenu="home", controller="addShows", action="popularShows")