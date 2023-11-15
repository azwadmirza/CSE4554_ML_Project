    def __init__(self, verbose=0, encoding='latin-1'):
        HTMLParser.__init__(self, verbose)
        self._reset()
        self.encoding = encoding

        if not PY2:
            # In Python 3 need to be defined explicitly
            def handle_starttag(tag, attrs):
                method = 'start_' + tag
                getattr(self, method, lambda x: None)(attrs)
            self.handle_starttag = handle_starttag

            def handle_endtag(tag):
                method = 'end_' + tag
                getattr(self, method, lambda: None)()
            self.handle_endtag = handle_endtag