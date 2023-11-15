    def filter(self, record):  # type: ignore
        # type: (SphinxWarningLogRecord) -> bool
        if isinstance(record, logging.LogRecord):
            record.__class__ = SphinxWarningLogRecord  # force subclassing to handle location

        location = getattr(record, 'location', None)
        if isinstance(location, tuple):
            docname, lineno = location
            if docname and lineno:
                record.location = '%s:%s' % (self.app.env.doc2path(docname), lineno)
            elif docname:
                record.location = '%s' % self.app.env.doc2path(docname)
            else:
                record.location = None
        elif isinstance(location, nodes.Node):
            record.location = get_node_location(location)
        elif location and ':' not in location:
            record.location = '%s' % self.app.env.doc2path(location)

        return True