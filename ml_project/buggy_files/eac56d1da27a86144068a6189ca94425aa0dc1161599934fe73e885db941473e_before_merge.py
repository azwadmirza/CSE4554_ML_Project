def encode_uri(uri):
    # type: (unicode) -> unicode
    split = list(urlsplit(uri))  # type: Any
    split[1] = split[1].encode('idna').decode('ascii')
    split[2] = quote_plus(split[2].encode('utf-8'), '/').decode('ascii')
    query = list((q, quote_plus(v.encode('utf-8')))
                 for (q, v) in parse_qsl(split[3]))
    split[3] = urlencode(query).decode('ascii')
    return urlunsplit(split)