    def _initialize_indices(self):
        """ Check each required index and make sure it exists, if it doesn't then create it """
        for index in self.natlasIndices:
            if not self.es.indices.exists(index):
                self.es.indices.create(index)

        # Avoid a race condition
        time.sleep(2)

        for index in self.natlasIndices:
            if self.esversion.match("<7.0.0"):
                self.es.indices.put_mapping(
                    index=index,
                    doc_type="_doc",
                    body=self.mapping,
                    include_type_name=True,
                )
            else:
                self.es.indices.put_mapping(
                    index=index,
                    body=self.mapping
                )