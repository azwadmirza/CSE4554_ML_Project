def _get_range_edges(first, last, offset, closed='left', base=0):
    if isinstance(offset, compat.string_types):
        offset = to_offset(offset)

    if isinstance(offset, Tick):
        is_day = isinstance(offset, Day)
        day_nanos = delta_to_nanoseconds(timedelta(1))

        # #1165
        if (is_day and day_nanos % offset.nanos == 0) or not is_day:
            return _adjust_dates_anchored(first, last, offset,
                                          closed=closed, base=base)

    if not isinstance(offset, Tick):  # and first.time() != last.time():
        # hack!
        first = first.normalize()
        last = last.normalize()

    if closed == 'left':
        first = Timestamp(offset.rollback(first))
    else:
        first = Timestamp(first - offset)

    last = Timestamp(last + offset)

    return first, last