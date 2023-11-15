    def parse_file(self, f, fname=None, verbosity=0, recurse=True):
        violations = []
        t0 = get_time()

        # Allow f to optionally be a raw string
        if isinstance(f, str):
            # Add it to a buffer if that's what we're doing
            f = StringIO(f)

        verbosity_logger("LEXING RAW ({0})".format(fname), verbosity=verbosity)
        # Lex the file and log any problems
        try:
            fs = FileSegment.from_raw(f.read())
        except SQLLexError as err:
            violations.append(err)
            fs = None

        if fs:
            verbosity_logger(fs.stringify(), verbosity=verbosity)

        t1 = get_time()
        verbosity_logger("PARSING ({0})".format(fname), verbosity=verbosity)
        # Parse the file and log any problems
        if fs:
            try:
                parsed = fs.parse(recurse=recurse, verbosity=verbosity, dialect=self.dialect)
            except SQLParseError as err:
                violations.append(err)
                parsed = None
            if parsed:
                verbosity_logger(frame_msg("Parsed Tree:"), verbosity=verbosity)
                verbosity_logger(parsed.stringify(), verbosity=verbosity)
        else:
            parsed = None

        t2 = get_time()
        time_dict = {'lexing': t1 - t0, 'parsing': t2 - t1}

        return parsed, violations, time_dict