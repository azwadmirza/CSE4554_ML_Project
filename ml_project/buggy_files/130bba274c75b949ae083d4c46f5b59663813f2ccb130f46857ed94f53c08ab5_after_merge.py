    def __str__(self):
        # for some fucking reason it's impossible to print self.field here, if someone figures out why please
        # tell me!
        valid = 'INVALID'
        if self.valid:
            valid = 'OK'
        return '<SeriesParser(data=%s,name=%s,id=%s,season=%s,season_pack=%s,episode=%s,quality=%s,proper=%s,' \
               'status=%s)>' % (self.data, self.name, str(self.id), self.season, self.season_pack, self.episode,
                                self.quality, self.proper_count, valid)