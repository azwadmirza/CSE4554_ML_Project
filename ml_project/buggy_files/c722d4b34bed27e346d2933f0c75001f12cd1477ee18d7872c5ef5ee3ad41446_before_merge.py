    def get_document_by_id(self, id: Union[str, UUID], index: Optional[str] = None) -> Document:
        index = index or self.index
        return self.indexes[index][id]