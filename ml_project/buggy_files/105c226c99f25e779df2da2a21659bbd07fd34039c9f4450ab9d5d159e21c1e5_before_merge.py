    def __init__(self, name, url='', api_key='0', cat_ids=None, default=False, search_mode='eponly',
                 search_fallback=False, enable_daily=True, enable_backlog=False, enable_manualsearch=False):
        """Initialize the class."""
        super(NewznabProvider, self).__init__(name)

        self.url = url
        self.api_key = api_key

        self.default = default

        self.search_mode = search_mode
        self.search_fallback = search_fallback
        self.enable_daily = enable_daily
        self.enable_manualsearch = enable_manualsearch
        self.enable_backlog = enable_backlog

        # 0 in the key spot indicates that no key is needed
        self.needs_auth = self.api_key != '0'
        self.public = not self.needs_auth

        self.cat_ids = cat_ids or ['5030', '5040']

        self.torznab = False

        self.params = False
        self.cap_tv_search = None
        self.providers_without_caps = ['gingadaddy', '6box']

        # For now apply the additional season search string for all newznab providers.
        # If we want to limited this per provider, I suggest using a dict, with provider: [list of season templates]
        # construction.
        self.season_templates = (
            'S{season:0>2}',  # example: 'Series.Name S03'
            'Season {season}',  # example: 'Series.Name Season 3'
        )

        self.cache = tv.Cache(self)