    def __str__(self):
        return "<%s(name=%s,id=%s,season=%s,episode=%s,quality=%s,proper=%s,status=%s)>" % \
               (self.__class__.__name__, self.name, self.id, self.season, self.episode,
                self.quality, self.proper_count, 'OK' if self.valid else 'INVALID')