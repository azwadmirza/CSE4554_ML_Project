    def identifier(self):
        """Return the episode identifier.

        :return:
        :rtype: string
        """
        if self.series.air_by_date and self.airdate != date.fromordinal(1):
            return self.airdate.strftime(dateFormat)
        if self.series.is_anime and self.absolute_number is not None:
            return 'e{0:02d}'.format(self.absolute_number)

        return 's{0:02d}e{1:02d}'.format(self.season, self.episode)