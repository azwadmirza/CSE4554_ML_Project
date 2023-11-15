    def __init__(self):
        self.entries = {}
        self.errors = {}
        self.total = StatsEntry(self, "Aggregated", None, use_response_times_cache=True)