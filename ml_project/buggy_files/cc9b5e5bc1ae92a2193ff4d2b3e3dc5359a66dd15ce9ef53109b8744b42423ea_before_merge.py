    def phash(self):
        # This isn't actually a predicate, it's just a infodict modifier that
        # injects ``traverse`` into the matchdict.  As a result, we don't
        # need to update the hash.
        return ''