    def get_all_documents_generator(
        self,
        index: Optional[str] = None,
        filters: Optional[Dict[str, List[str]]] = None,
        return_embedding: Optional[bool] = None,
        batch_size: int = 10_000,
    ) -> Generator[Document, None, None]:
        """
        Get documents from the document store. Under-the-hood, documents are fetched in batches from the
        document store and yielded as individual documents. This method can be used to iteratively process
        a large number of documents without having to load all documents in memory.

        :param index: Name of the index to get the documents from. If None, the
                      DocumentStore's default index (self.index) will be used.
        :param filters: Optional filters to narrow down the documents to return.
                        Example: {"name": ["some", "more"], "category": ["only_one"]}
        :param return_embedding: Whether to return the document embeddings.
        """

        index = index or self.index
        # Generally ORM objects kept in memory cause performance issue
        # Hence using directly column name improve memory and performance.
        # Refer https://stackoverflow.com/questions/23185319/why-is-loading-sqlalchemy-objects-via-the-orm-5-8x-slower-than-rows-via-a-raw-my
        documents_query = self.session.query(
            DocumentORM.id,
            DocumentORM.text,
            DocumentORM.vector_id
        ).filter_by(index=index)

        if filters:
            documents_query = documents_query.join(MetaORM)
            for key, values in filters.items():
                documents_query = documents_query.filter(
                    MetaORM.name == key,
                    MetaORM.value.in_(values),
                    DocumentORM.id == MetaORM.document_id
                )

        documents_map = {}
        for i, row in enumerate(self._windowed_query(documents_query, DocumentORM.id, batch_size), start=1):
            documents_map[row.id] = Document(
                id=row.id,
                text=row.text,
                meta=None if row.vector_id is None else {"vector_id": row.vector_id}  # type: ignore
            )
            if i % batch_size == 0:
                documents_map = self._get_documents_meta(documents_map)
                yield from documents_map.values()
                documents_map = {}
        if documents_map:
            documents_map = self._get_documents_meta(documents_map)
            yield from documents_map.values()