    def add_document(self, pagename, filename, title, text):
        self.database.begin_transaction()
        # sphinx_page_path is used to easily retrieve documents by path.
        sphinx_page_path = '"sphinxpagepath%s"' % pagename.replace('/', '_')
        # Delete the old document if it exists.
        self.database.delete_document(sphinx_page_path)

        doc = xapian.Document()
        doc.set_data(text)
        doc.add_value(self.DOC_PATH, pagename)
        doc.add_value(self.DOC_TITLE, title)
        self.indexer.set_document(doc)
        self.indexer.index_text(text)
        doc.add_term(sphinx_page_path)
        for word in text.split():
            doc.add_posting(word, 1)
        self.database.add_document(doc)
        self.database.commit_transaction()