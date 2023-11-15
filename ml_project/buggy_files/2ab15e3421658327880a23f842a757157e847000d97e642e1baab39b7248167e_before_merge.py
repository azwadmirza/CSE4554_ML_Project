    def __location_set(self, location):
        "Set location, checking for loops and allowing dbref"
        if isinstance(location, (basestring, int)):
            # allow setting of #dbref
            dbid = dbref(location, reqhash=False)
            if dbid:
                try:
                    location = ObjectDB.objects.get(id=dbid)
                except ObjectDoesNotExist:
                    # maybe it is just a name that happens to look like a dbid
                    pass
        try:
            def is_loc_loop(loc, depth=0):
                "Recursively traverse target location, trying to catch a loop."
                if depth > 10:
                    return
                elif loc == self:
                    raise RuntimeError
                elif loc == None:
                    raise RuntimeWarning
                return is_loc_loop(loc.db_location, depth + 1)
            try:
                is_loc_loop(location)
            except RuntimeWarning:
                pass

            # if we get to this point we are ready to change location

            old_location = self.db_location

            # this is checked in _db_db_location_post_save below
            self._safe_contents_update = True

            # actually set the field (this will error if location is invalid)
            self.db_location = location
            self.save(update_fields=["db_location"])

            # remove the safe flag
            del self._safe_contents_update

            # update the contents cache
            if old_location:
                old_location.contents_cache.remove(self)
            if self.db_location:
                self.db_location.contents_cache.add(self)

        except RuntimeError:
            errmsg = "Error: %s.location = %s creates a location loop." % (self.key, location)
            logger.log_trace(errmsg)
            raise
        except Exception as e:
            errmsg = "Error (%s): %s is not a valid location." % (str(e), location)
            logger.log_trace(errmsg)
            raise