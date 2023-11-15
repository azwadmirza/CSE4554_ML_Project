def parse_match_logging(parse_depth, match_depth, match_segment, grammar,
                        func, msg, verbosity, v_level, **kwargs):
    s = "[PD:{0} MD:{1}]\t{2:<50}\t{3:<20}".format(
        parse_depth, match_depth, ('.' * match_depth) + str(match_segment),
        "{0}.{1} {2}".format(grammar, func, msg)
    )
    if kwargs:
        s += "\t[{0}]".format(
            ', '.join(["{0}={1}".format(
                k, repr(v) if isinstance(v, str) else v) for k, v in kwargs.items()])
        )
    verbosity_logger(s, verbosity, v_level=v_level)