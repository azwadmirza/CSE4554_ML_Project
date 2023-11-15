    def __init__(
        self,
        url: str = "sqlite://",
        index: str = "document",
        label_index: str = "label",
        update_existing_documents: bool = False,
    ):
        """
        An SQL backed DocumentStore. Currently supports SQLite, PostgreSQL and MySQL backends.

        :param url: URL for SQL database as expected by SQLAlchemy. More info here: https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls
        :param index: The documents are scoped to an index attribute that can be used when writing, querying, or deleting documents. 
                      This parameter sets the default value for document index.
        :param label_index: The default value of index attribute for the labels.
        :param update_existing_documents: Whether to update any existing documents with the same ID when adding
                                          documents. When set as True, any document with an existing ID gets updated.
                                          If set to False, an error is raised if the document ID of the document being
                                          added already exists. Using this parameter could cause performance degradation
                                          for document insertion.
        """
        engine = create_engine(url)
        ORMBase.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.index = index
        self.label_index = label_index
        self.update_existing_documents = update_existing_documents
        if getattr(self, "similarity", None) is None:
            self.similarity = None