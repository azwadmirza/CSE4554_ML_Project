def _adjust_dates_anchored(first, last, offset, closed='right', base=0):
    from pandas.tseries.tools import normalize_date

    start_day_nanos = Timestamp(normalize_date(first)).value
    last_day_nanos = Timestamp(normalize_date(last)).value

    base_nanos = (base % offset.n) * offset.nanos // offset.n
    start_day_nanos += base_nanos
    last_day_nanos += base_nanos

    foffset = (first.value - start_day_nanos) % offset.nanos
    loffset = (last.value - last_day_nanos) % offset.nanos

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

    return (Timestamp(fresult, tz=first.tz),
            Timestamp(lresult, tz=last.tz))