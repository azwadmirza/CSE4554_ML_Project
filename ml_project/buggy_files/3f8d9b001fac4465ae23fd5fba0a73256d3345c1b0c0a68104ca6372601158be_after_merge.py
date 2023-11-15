    def __init__(self, sourcef, incfile=False, widthcount=0):
        ''' Process a file and decorate the resultant Preprocess instance with
            self.result (the preprocessed file) and self.styles (extracted stylesheet
            information) for the caller.
        '''

        # fix keywords dict for use by the parser.
        self.keywords = dict([(x + '::', getattr(self, 'handle_' + x)) for x in self.keywords])

        self.widthcount = widthcount

        name = sourcef.name
        source = sourcef.read()
        if isinstance(source, bytes):
            source = source.decode('utf8')
        source = source.replace('\r\n', '\n').replace('\r', '\n')

        # Make the determination if an include file is a stylesheet or
        # another restructured text file, and handle stylesheets appropriately.

        if incfile:
            try:
                self.styles = styles = rson_loads(source)
                substyles = styles.get('styles')
                if substyles is not None:
                    styles['styles'] = dict(substyles)
            except:
                pass
            else:
                self.changed = True
                self.keep = False
                return

        # Read the whole file and wrap it in a DummyFile
        self.sourcef = DummyFile(name, source)

        # Use a regular expression on the source, to take it apart
        # and put it back together again.
        self.source = source = [x for x in self.splitter(source) if x]
        self.result = result = []
        self.styles = {}
        self.changed = False

        # More efficient to pop() a list than to keep taking tokens from [0]
        source.reverse()
        isblank = False
        keywords = self.keywords
        handle_single = keywords['single::']
        while source:
            wasblank = isblank
            isblank = False
            chunk = source.pop()
            result.append(chunk)

            # Only process single lines
            if not chunk.endswith('\n'):
                continue
            result[-1] = chunk[:-1]
            if chunk.index('\n') != len(chunk)-1:
                continue

            # Parse the line to look for one of our keywords.
            tokens = chunk.split()
            isblank = not tokens
            if len(tokens) >= 2 and tokens[0] == '..' and tokens[1].endswith('::'):
                func = keywords.get(tokens[1])
                if func is None:
                    continue
                chunk = chunk.split('::', 1)[1]
            elif wasblank and len(tokens) == 1 and chunk[0].isalpha() and tokens[0].isalpha():
                func = handle_single
                chunk = tokens[0]
            else:
                continue

            result.pop()
            func(chunk.strip())

        # Determine if we actually did anything or not.  Just use our source file
        # if not.  Otherwise, write the results to disk (so the user can use them
        # for debugging) and return them.
        if self.changed:
            result.append('')
            result = DummyFile(name + '.build_temp', '\n'.join(result))
            self.keep = keep = len(result.read().strip())
            if keep:
                f = open(result.name, 'w')
                # Can call read a second time here because it's a DummyFile:
                f.write(result.read())
                f.close()
            self.result = result
        else:
            self.result = self.sourcef