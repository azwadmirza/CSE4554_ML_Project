    def isincfile(self):
        """Return true if path indicates increment, sets various variables"""
        if not self.index:  # consider the last component as quoted
            dirname, basename = self.dirsplit()
            temp_rp = rpath.RPath(self.conn, dirname, (unquote(basename), ))
            result = temp_rp.isincfile()
            if result:
                self.inc_basestr = unquote(temp_rp.inc_basestr)
                self.inc_timestr = unquote(temp_rp.inc_timestr)
        else:
            result = rpath.RPath.isincfile(self)
        return result