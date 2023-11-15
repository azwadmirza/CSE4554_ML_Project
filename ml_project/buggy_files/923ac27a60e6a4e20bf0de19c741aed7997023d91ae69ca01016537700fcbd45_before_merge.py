    def _insert_column(self, key):
        self.columns = Index(np.concatenate((self.columns, [key])))