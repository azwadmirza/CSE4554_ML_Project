    def bounds(self):
        """Returns minimum bounding region (minx, miny, maxx, maxy)"""
        try:
            xy = self.coords[0]
        except IndexError:
            return ()
        return (xy[0], xy[1], xy[0], xy[1])