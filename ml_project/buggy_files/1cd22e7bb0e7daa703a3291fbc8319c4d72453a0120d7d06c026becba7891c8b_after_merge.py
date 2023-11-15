        def get_magnet(self):
            return ("magnet:?xt=urn:btih:%s&dn=%s" %
                    (str(self.infohash).encode('hex'), self.title)) + \
                   ("&tr=%s" % self.tracker_info if self.tracker_info else "")