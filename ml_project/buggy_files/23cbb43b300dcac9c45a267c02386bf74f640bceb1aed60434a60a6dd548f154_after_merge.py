    def get_document_by_id(self, id: str, index=None) -> Optional[Document]:
        if index is None:
            index = self.index
        query = {"query": {"ids": {"values": [id]}}}
        result = self.client.search(index=index, body=query)["hits"]["hits"]

        document = self._convert_es_hit_to_document(result[0]) if result else None
        return document