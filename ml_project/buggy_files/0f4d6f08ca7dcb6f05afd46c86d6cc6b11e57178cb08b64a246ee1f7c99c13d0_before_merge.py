def format_range(value):
    """Formats a range header tuple per the HTTP spec.

    Args:
        value: ``tuple`` passed to `req.range`
    """

    # PERF(kgriffs): % was found to be faster than str.format(),
    # string concatenation, and str.join() in this case.

    if len(value) == 4:
        return '%s %s-%s/%s' % (value[3], value[0], value[1], value[2])

    return 'bytes %s-%s/%s' % (value[0], value[1], value[2])