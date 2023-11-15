    def box(self, left_edge, right_edge, **kwargs):
        """
        box is a wrapper to the Region object for creating a region
        without having to specify a *center* value.  It assumes the center
        is the midpoint between the left_edge and right_edge.
        """
        # we handle units in the region data object
        # but need to check if left_edge or right_edge is a
        # list or other non-array iterable before calculating
        # the center
        if isinstance(left_edge[0], YTQuantity):
            left_edge = YTArray(left_edge)
            right_edge = YTArray(right_edge)

        left_edge = np.asanyarray(left_edge, dtype='float64')
        right_edge = np.asanyarray(right_edge, dtype='float64')
        c = (left_edge + right_edge)/2.0
        return self.region(c, left_edge, right_edge, **kwargs)