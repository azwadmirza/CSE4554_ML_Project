def _adjust_dates_anchored(first, last, offset, closed='right', base=0):
    # First and last offsets should be calculated from the start day to fix an
    # error cause by resampling across multiple days when a one day period is
    # not a multiple of the frequency.
    #
    # See https://github.com/pandas-dev/pandas/issues/8683

    # 14682 - Since we need to drop the TZ information to perform
    # the adjustment in the presence of a DST change,
    # save TZ Info and the DST state of the first and last parameters
    # so that we can accurately rebuild them at the end.
    first_tzinfo = first.tzinfo
    last_tzinfo = last.tzinfo
    first_dst = bool(first.dst())
    last_dst = bool(last.dst())

    first = first.tz_localize(None)
    last = last.tz_localize(None)

    start_day_nanos = first.normalize().value

    base_nanos = (base % offset.n) * offset.nanos // offset.n
    start_day_nanos += base_nanos

    foffset = (first.value - start_day_nanos) % offset.nanos
    loffset = (last.value - start_day_nanos) % offset.nanos

    if closed == 'right':
        if foffset > 0:
            # roll back
            fresult = first.value - foffset
        else:
            fresult = first.value - offset.nanos

        if loffset > 0:
            # roll forward
            lresult = last.value + (offset.nanos - loffset)
        else:
            # already the end of the road
            lresult = last.value
    else:  # closed == 'left'
        if foffset > 0:
            fresult = first.value - foffset
        else:
            # start of the road
            fresult = first.value

        if loffset > 0:
            # roll forward
            lresult = last.value + (offset.nanos - loffset)
        else:
            lresult = last.value + offset.nanos

    return (Timestamp(fresult).tz_localize(first_tzinfo, ambiguous=first_dst),
            Timestamp(lresult).tz_localize(last_tzinfo, ambiguous=last_dst))