    def __init__(self, encodings=None, exception: UnicodeDecodeError = None,
                 object = None):
        self.object = object
        suffix = []
        if encodings:
            suffix.append("with given encodings %r" % encodings)
        if exception:
            suffix.append('at position %s with length %d (%r)'
                          '' % (exception.start, exception.end,
                                exception.object[exception.start:exception.end]))
            suffix.append('with reason %r' % exception.reason)
        suffix = (' ' + ' '.join(suffix)) if suffix else ''
        super().__init__("Could not decode string%s." % suffix)