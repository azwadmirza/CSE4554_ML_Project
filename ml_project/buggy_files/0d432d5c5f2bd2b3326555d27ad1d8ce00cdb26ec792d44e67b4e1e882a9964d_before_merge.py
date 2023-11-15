    def to_csv(self, path, index=True):
        """
        Write the Series to a CSV file

        Parameters
        ----------
        path : string or None
            Output filepath. If None, write to stdout
        index : bool, optional
            Include the index as row names or not
        """
        f = open(path, 'w')
        csvout = csv.writer(f, lineterminator='\n')
        csvout.writerows(self.iteritems(index))
        f.close()