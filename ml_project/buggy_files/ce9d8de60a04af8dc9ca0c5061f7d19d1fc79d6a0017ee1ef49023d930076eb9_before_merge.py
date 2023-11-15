    def expand(segments, recurse=True, parse_depth=0, verbosity=0, dialect=None):
        segs = tuple()
        for stmt in segments:
            try:
                if not stmt.is_expandable:
                    logging.info("[PD:{0}] Skipping expansion of {1}...".format(parse_depth, stmt))
                    segs += stmt,
                    continue
            except Exception as err:
                # raise ValueError("{0} has no attribute `is_expandable`. This segment appears poorly constructed.".format(stmt))
                logging.error("{0} has no attribute `is_expandable`. This segment appears poorly constructed.".format(stmt))
                raise err
            if not hasattr(stmt, 'parse'):
                raise ValueError("{0} has no method `parse`. This segment appears poorly constructed.".format(stmt))
            parse_depth_msg = "Parse Depth {0}. Expanding: {1}: {2!r}".format(
                parse_depth, stmt.__class__.__name__,
                curtail_string(stmt.raw, length=40))
            verbosity_logger(frame_msg(parse_depth_msg), verbosity=verbosity)
            res = stmt.parse(recurse=recurse, parse_depth=parse_depth, verbosity=verbosity, dialect=dialect)
            if isinstance(res, BaseSegment):
                segs += (res,)
            else:
                # We might get back an iterable of segments
                segs += tuple(res)
        # Basic Validation
        check_still_complete(segments, segs, tuple())
        return segs