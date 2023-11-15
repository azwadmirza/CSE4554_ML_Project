    def get_index_from_key(self, key):
        try:
            return self.createIndex(self.keys.index(key), 0)
        except ValueError:
            return QModelIndex()