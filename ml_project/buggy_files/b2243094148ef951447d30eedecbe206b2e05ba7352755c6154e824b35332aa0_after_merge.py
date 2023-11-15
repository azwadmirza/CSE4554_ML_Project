    def __str__(self):
        valid = 'OK' if self.valid else 'INVALID'
        return '<SeriesParseResult(data=%s,name=%s,id=%s,season=%s,season_pack=%s,episode=%s,quality=%s,proper=%s,' \
               'special=%s,status=%s)>' % \
               (self.data, self.name, str(self.id), self.season, self.season_pack, self.episode, self.quality,
                self.proper_count, self.special, valid)