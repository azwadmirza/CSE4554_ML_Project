    def transform(self, data: DataEntry) -> DataEntry:
        for field in self.fields:
            data[field] = self.swap(data[field])
        return data