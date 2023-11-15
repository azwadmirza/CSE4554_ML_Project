        def convert(x):
            if isinstance(x, unicode):
                return x
            elif isinstance(x, BASESTRING):
                return x.decode('utf8', 'ignore')
            else:
                self.fail('must be a list of strings', view, True)