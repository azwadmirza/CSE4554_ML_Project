def parse_txt_dict(data, msg):
    """Parse DNS TXT record containing a dict."""
    output = {}
    txt, _ = qname_decode(data, msg, raw=True)
    for prop in txt:
        key, value = prop.split(b'=', 1)
        output[key] = value
    return output