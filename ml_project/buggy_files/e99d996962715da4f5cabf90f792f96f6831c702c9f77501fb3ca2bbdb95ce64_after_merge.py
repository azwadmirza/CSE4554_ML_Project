def parse_match_logging(grammar, func, msg, parse_context, v_level, **kwargs):
    s = "[PD:{0} MD:{1}]\t{2:<50}\t{3:<20}".format(
        parse_context.parse_depth, parse_context.match_depth,
        ('.' * parse_context.match_depth) + str(parse_context.match_segment),
        "{0}.{1} {2}".format(grammar, func, msg)
    )
    if kwargs:
        s += "\t[{0}]".format(
            ', '.join(["{0}={1}".format(
                k, repr(v) if isinstance(v, str) else v) for k, v in kwargs.items()])
        )
    verbosity_logger(s, parse_context.verbosity, v_level=v_level)