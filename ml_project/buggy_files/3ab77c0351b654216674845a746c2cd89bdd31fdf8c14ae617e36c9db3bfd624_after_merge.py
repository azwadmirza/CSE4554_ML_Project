    def __init__(self):
        """Initialize the trakt recommended list object."""
        self.cache_subfolder = __name__.split('.')[-1] if '.' in __name__ else __name__
        self.session = requests.Session()
        self.recommender = "Trakt Popular"
        self.default_img_src = 'trakt-default.png'
        self.anidb = Anidb(cache_dir=app.CACHE_DIR)
        self.tvdb_api_v2 = get_tvdbv2_api()