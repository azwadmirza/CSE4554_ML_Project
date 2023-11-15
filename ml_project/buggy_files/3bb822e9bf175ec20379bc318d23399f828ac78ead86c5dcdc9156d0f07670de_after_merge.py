def parse_timedelta(
    argument: str,
    *,
    maximum: Optional[timedelta] = None,
    minimum: Optional[timedelta] = None,
    allowed_units: Optional[List[str]] = None,
) -> Optional[timedelta]:
    """
    This converts a user provided string into a timedelta

    The units should be in order from largest to smallest.
    This works with or without whitespace.

    Parameters
    ----------
    argument : str
        The user provided input
    maximum : Optional[timedelta]
        If provided, any parsed value higher than this will raise an exception
    minimum : Optional[timedelta]
        If provided, any parsed value lower than this will raise an exception
    allowed_units : Optional[List[str]]
        If provided, you can constrain a user to expressing the amount of time
        in specific units. The units you can chose to provide are the same as the
        parser understands. (``weeks``, ``days``, ``hours``, ``minutes``, ``seconds``)

    Returns
    -------
    Optional[timedelta]
        If matched, the timedelta which was parsed. This can return `None`

    Raises
    ------
    BadArgument
        If the argument passed uses a unit not allowed, but understood
        or if the value is out of bounds.
    """
    matches = TIME_RE.match(argument)
    allowed_units = allowed_units or ["weeks", "days", "hours", "minutes", "seconds"]
    if matches:
        params = {k: int(v) for k, v in matches.groupdict().items() if v is not None}
        for k in params.keys():
            if k not in allowed_units:
                raise BadArgument(
                    _("`{unit}` is not a valid unit of time for this command").format(unit=k)
                )
        if params:
            try:
                delta = timedelta(**params)
            except OverflowError:
                raise BadArgument(
                    _("The time set is way too high, consider setting something reasonable.")
                )
            if maximum and maximum < delta:
                raise BadArgument(
                    _(
                        "This amount of time is too large for this command. (Maximum: {maximum})"
                    ).format(maximum=humanize_timedelta(timedelta=maximum))
                )
            if minimum and delta < minimum:
                raise BadArgument(
                    _(
                        "This amount of time is too small for this command. (Minimum: {minimum})"
                    ).format(minimum=humanize_timedelta(timedelta=minimum))
                )
            return delta
    return None