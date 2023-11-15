    def warn_and_replace(self, error):
        """Custom decoding error handler that warns and replaces."""
        linestart = error.object.rfind('\n', 0, error.start)
        lineend = error.object.find('\n', error.start)
        if lineend == -1: lineend = len(error.object)
        lineno = error.object.count('\n', 0, error.start) + 1
        self.warn(self.docname, 'undecodable source characters, '
                  'replacing with "?": %r' %
                  (error.object[linestart+1:error.start] + '>>>' +
                   error.object[error.start:error.end] + '<<<' +
                   error.object[error.end:lineend]), lineno)
        return (u'?', error.end)