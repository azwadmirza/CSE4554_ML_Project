        def get_magnet(self):
            return ("magnet:?xt=urn:btih:%s&dn=%s" %
                    (str(self.infohash).encode('hex'), str(self.title).encode('utf8'))) + \
                   ("&tr=%s" % (str(self.tracker_info).encode('utf8')) if self.tracker_info else "")