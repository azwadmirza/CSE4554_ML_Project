    def __init__(self, num_seasons: int, time_feature: TimeFeature) -> None:
        super(SeasonalityISSM, self).__init__()
        self.num_seasons = num_seasons
        self.time_feature = time_feature