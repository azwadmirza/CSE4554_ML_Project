    def __init__(self, intent, source=None, title="", score=0.0):
        self._intent = intent  # user's original intent to Vis
        self._inferred_intent = intent  # re-written, expanded version of user's original intent
        self._source = source  # original data attached to the Vis
        self._vis_data = None  # processed data for Vis (e.g., selected, aggregated, binned)
        self._code = None
        self._mark = ""
        self._min_max = {}
        self._postbin = None
        self.title = title
        self.score = score
        self.refresh_source(self._source)