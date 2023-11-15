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
            (source, line) = get_source_line(location)
            if source and line:
                record.location = "%s:%s" % (source, line)
            elif source:
                record.location = "%s:" % source
            elif line:
                record.location = "<unknown>:%s" % line
            else:
                record.location = None
        elif location and ':' not in location:
            record.location = '%s' % self.app.env.doc2path(location)

        return True