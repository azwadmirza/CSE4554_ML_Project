def parse_tracker_url(tracker_url):
    # get tracker type
    if tracker_url.startswith(u'http'):
        tracker_type = u'HTTP'
    elif tracker_url.startswith(u'udp'):
        tracker_type = u'UDP'
    else:
        raise MalformedTrackerURLException(u'Unexpected tracker type (%s).' % tracker_url)

    # get URL information
    url_fields = tracker_url.split(u'://')[1]
    # some UDP trackers may not have 'announce' at the end.
    if url_fields.find(u'/') == -1:
        if tracker_type == u'UDP':
            hostname_part = url_fields
            announce_page = None
        else:
            raise MalformedTrackerURLException(u'Invalid tracker URL (%s).' % tracker_url)
    else:
        hostname_part, announce_page = url_fields.split(u'/', 1)

    # get port number if exists, otherwise, use HTTP default 80
    if hostname_part.find(u':') != -1:
        hostname, port = hostname_part.split(u':', 1)
        port = int(port)
    elif tracker_type == u'HTTP':
        hostname = hostname_part
        port = 80
    else:
        raise MalformedTrackerURLException(u'No port number for UDP tracker URL (%s).' % tracker_url)

    return tracker_type, (hostname, port), announce_page