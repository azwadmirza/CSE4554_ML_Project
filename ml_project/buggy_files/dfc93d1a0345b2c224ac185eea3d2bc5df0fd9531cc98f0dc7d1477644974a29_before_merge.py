def wait_for_successful_query(name, wait_for=300, **kwargs):
    '''
    Like query but, repeat and wait until match/match_type or status is fulfilled. State returns result from last
    query state in case of success or if no successful query was made within wait_for timeout.

    request_interval
        Optional interval to delay requests by N seconds to reduce the number of requests sent.
    '''
    starttime = time.time()

    while True:
        caught_exception = None
        ret = None
        try:
            ret = query(name, wait_for=wait_for, **kwargs)
            if ret['result']:
                return ret
        except Exception as exc:
            caught_exception = exc

        if time.time() > starttime + wait_for:
            if not ret and caught_exception:
                # workaround pylint bug https://www.logilab.org/ticket/3207
                raise caught_exception  # pylint: disable=E0702
            return ret
        else:
            # Space requests out by delaying for an interval
            if 'request_interval' in kwargs:
                log.debug("delaying query for {0} seconds.".format(kwargs['request_interval']))
                time.sleep(kwargs['request_interval'])