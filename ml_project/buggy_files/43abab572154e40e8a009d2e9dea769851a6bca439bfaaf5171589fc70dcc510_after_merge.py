    def lessThan(self, left, right):
        """
        Implements ordering in a natural way, as a human would sort.
        This functions enables sorting of the main variable editor table,
        which does not rely on 'self.sort()'.
        """
        leftData = self.sourceModel().data(left)
        rightData = self.sourceModel().data(right)
        try:
            if isinstance(leftData, str) and isinstance(rightData, str):
                return natsort(leftData) < natsort(rightData)
            else:
                return leftData < rightData
        except TypeError:
            # This is needed so all the elements that cannot be compared such
            # as dataframes and numpy arrays are grouped together in the
            # variable explorer. For more info see spyder-ide/spyder#14527
            return True