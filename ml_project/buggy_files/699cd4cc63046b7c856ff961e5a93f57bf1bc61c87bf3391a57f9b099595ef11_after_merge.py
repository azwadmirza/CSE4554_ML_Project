def rebuild_censored_list():
    """Rebuild the censored list."""
    # set of censored items
    results = set()
    for value in itervalues(censored_items):
        if not value:
            continue
        if isinstance(value, collections.Iterable) and not isinstance(value, string_types):
            for item in value:
                if item and item != '0':
                    results.add(item)
        elif value and value != '0':
            results.add(value)

    def quote_unicode(value):
        """Quote a unicode value by encoding it to bytes first."""
        if isinstance(value, text_type):
            return quote(value.encode(default_encoding, 'replace'))
        return quote(value)

    # set of censored items and urlencoded counterparts
    results |= {quote_unicode(item) for item in results}
    # convert set items to unicode and typecast to list
    results = list({item.decode(default_encoding, 'replace')
                    if not isinstance(item, text_type) else item for item in results})
    # sort the list in order of descending length so that entire item is censored
    # e.g. password and password_1 both get censored instead of getting ********_1
    results.sort(key=len, reverse=True)

    # replace
    censored[:] = results