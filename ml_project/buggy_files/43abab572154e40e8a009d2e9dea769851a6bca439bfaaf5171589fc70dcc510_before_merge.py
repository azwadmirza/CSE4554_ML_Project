    def lessThan(self, left, right):
        """
        Implements ordering in a natural way, as a human would sort.
        This functions enables sorting of the main variable editor table,
        which does not rely on 'self.sort()'.
        """
        leftData = self.sourceModel().data(left)
        rightData = self.sourceModel().data(right)
        if isinstance(leftData, str) and isinstance(rightData, str):
            return natsort(leftData) < natsort(rightData)
        else:
            return leftData < rightData