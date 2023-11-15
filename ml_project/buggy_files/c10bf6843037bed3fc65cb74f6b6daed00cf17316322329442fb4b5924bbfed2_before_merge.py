    def get_from_freq(cls, freq: str, add_trend: bool = DEFAULT_ADD_TREND):
        offset = to_offset(freq)

        seasonal_issms: List[SeasonalityISSM] = []

        if offset.name == "M":
            seasonal_issms = [
                SeasonalityISSM(num_seasons=12)  # month-of-year seasonality
            ]
        elif offset.name == "W-SUN":
            seasonal_issms = [
                SeasonalityISSM(num_seasons=53)  # week-of-year seasonality
            ]
        elif offset.name == "D":
            seasonal_issms = [
                SeasonalityISSM(num_seasons=7)
            ]  # day-of-week seasonality
        elif offset.name == "B":  # TODO: check this case
            seasonal_issms = [
                SeasonalityISSM(num_seasons=7)
            ]  # day-of-week seasonality
        elif offset.name == "H":
            seasonal_issms = [
                SeasonalityISSM(num_seasons=24),  # hour-of-day seasonality
                SeasonalityISSM(num_seasons=7),  # day-of-week seasonality
            ]
        elif offset.name == "T":
            seasonal_issms = [
                SeasonalityISSM(num_seasons=60),  # minute-of-hour seasonality
                SeasonalityISSM(num_seasons=24),  # hour-of-day seasonality
            ]
        else:
            RuntimeError(f"Unsupported frequency {offset.name}")

        return cls(seasonal_issms=seasonal_issms, add_trend=add_trend)