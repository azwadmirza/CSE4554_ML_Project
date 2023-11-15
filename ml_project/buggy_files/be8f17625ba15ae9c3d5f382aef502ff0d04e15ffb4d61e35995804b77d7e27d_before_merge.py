    def get_document_by_id(self, id: UUID, index=None) -> Optional[Document]:
        index = index or self.index
        document_row = self.session.query(DocumentORM).filter_by(index=index, id=id).first()
        document = document_row or self._convert_sql_row_to_document(document_row)
        return document