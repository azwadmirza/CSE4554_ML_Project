    def as_matrix(self, columns=None):
        """
        Convert the frame to its Numpy-array matrix representation

        Columns are presented in sorted order unless a specific list
        of columns is provided.
        """
        if columns is None:
            columns = self.columns

        if len(columns) == 0:
            return np.zeros((len(self.index), 0), dtype=float)

        return np.array([self.icol(i).values
                         for i in range(len(self.columns))]).T