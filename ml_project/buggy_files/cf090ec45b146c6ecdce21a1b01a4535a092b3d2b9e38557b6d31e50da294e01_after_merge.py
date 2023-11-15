    def getTrendingShows(self, traktList=None):
        """
        Display the new show page which collects a tvdb id, folder, and extra options and
        posts them to addNewShow
        """
        e = None
        t = PageTemplate(rh=self, filename="addShows_recommended.mako")
        if traktList is None:
            traktList = ""

        traktList = traktList.lower()

        if traktList == "trending":
            page_url = "shows/trending"
        elif traktList == "popular":
            page_url = "shows/popular"
        elif traktList == "anticipated":
            page_url = "shows/anticipated"
        elif traktList == "collected":
            page_url = "shows/collected"
        elif traktList == "watched":
            page_url = "shows/watched"
        elif traktList == "played":
            page_url = "shows/played"
        elif traktList == "recommended":
            page_url = "recommendations/shows"
        elif traktList == "newshow":
            page_url = 'calendars/all/shows/new/%s/30' % datetime.date.today().strftime("%Y-%m-%d")
        elif traktList == "newseason":
            page_url = 'calendars/all/shows/premieres/%s/30' % datetime.date.today().strftime("%Y-%m-%d")
        else:
            page_url = "shows/anticipated"

        try:
            (trakt_blacklist, recommended_shows, removed_from_medusa) = TraktPopular().fetch_popular_shows(page_url=page_url, trakt_list=traktList)
        except Exception as e:
            # print traceback.format_exc()
            trakt_blacklist = False
            recommended_shows = None
            removed_from_medusa = None

        return t.render(trakt_blacklist=trakt_blacklist, recommended_shows=recommended_shows, removed_from_medusa=removed_from_medusa,
                        exception=e, enable_anime_options=False, blacklist=[], whitelist=[])