    def __init__(self, intent, source=None, title="", score=0.0):
        self._intent = intent  # This is the user's original intent to Vis
        self._inferred_intent = intent  # This is the re-written, expanded version of user's original intent (include inferred vis info)
        self._source = source  # This is the original data that is attached to the Vis
        self._vis_data = (
            None  # This is the data that represents the Vis (e.g., selected, aggregated, binned)
        )
        self._code = None
        self._mark = ""
        self._min_max = {}
        self._postbin = None
        self.title = title
        self.score = score
        self.refresh_source(self._source)