    def get_from_freq(cls, freq: str, add_trend: bool = DEFAULT_ADD_TREND):
        offset = to_offset(freq)

        seasonal_issms: List[SeasonalityISSM] = []

        if offset.name == "M":
            seasonal_issms = [MonthOfYearSeasonalISSM()]
        elif offset.name == "W-SUN":
            seasonal_issms = [WeekOfYearSeasonalISSM()]
        elif offset.name == "D":
            seasonal_issms = [DayOfWeekSeasonalISSM()]
        elif offset.name == "B":  # TODO: check this case
            seasonal_issms = [DayOfWeekSeasonalISSM()]
        elif offset.name == "H":
            seasonal_issms = [
                HourOfDaySeasonalISSM(),
                DayOfWeekSeasonalISSM(),
            ]
        elif offset.name == "T":
            seasonal_issms = [
                MinuteOfHourSeasonalISSM(),
                HourOfDaySeasonalISSM(),
            ]
        else:
            RuntimeError(f"Unsupported frequency {offset.name}")

        return cls(seasonal_issms=seasonal_issms, add_trend=add_trend)