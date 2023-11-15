    def season(self):
        return 1 if not self.parsed_season and self.allow_seasonless else self.parsed_season