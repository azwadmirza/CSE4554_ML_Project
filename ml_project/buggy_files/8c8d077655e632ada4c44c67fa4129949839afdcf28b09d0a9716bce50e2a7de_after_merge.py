    def warn_and_replace(self, error):
        """Custom decoding error handler that warns and replaces."""
        linestart = error.object.rfind(b'\n', 0, error.start)
        lineend = error.object.find(b'\n', error.start)
        if lineend == -1: lineend = len(error.object)
        lineno = error.object.count(b'\n', 0, error.start) + 1
        self.warn(self.docname, 'undecodable source characters, '
                  'replacing with "?": %r' %
                  (error.object[linestart+1:error.start] + b'>>>' +
                   error.object[error.start:error.end] + b'<<<' +
                   error.object[error.end:lineend]), lineno)
        return (u'?', error.end)