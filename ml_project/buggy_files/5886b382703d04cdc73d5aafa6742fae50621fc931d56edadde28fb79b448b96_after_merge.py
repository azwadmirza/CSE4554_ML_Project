def create_valid_metainfo(metainfo):
    """
    Creates a valid metainfo dictionary by validating the elements and correcting when possible.

    :param metainfo: the metainfo that has to be validated
    :return: the original metainfo with corrected elements if possible
    :raise ValueError: if there is a faulty element which cannot be corrected.
    """
    metainfo_result = metainfo

    if not isinstance(metainfo, DictType):
        raise ValueError('metainfo not dict')

    # some .torrent files have a dht:// url in the announce field.
    if ('announce' in metainfo and metainfo['announce']) \
            and (not (is_valid_url(metainfo['announce']) or metainfo['announce'].startswith('dht:'))):
        raise ValueError('announce URL bad')

    # common additional fields
    if 'announce-list' in metainfo:
        al = metainfo['announce-list']
        if not isinstance(al, ListType):
            raise ValueError('announce-list is not list, but ' + repr(type(al)))
        if not all(isinstance(tier, ListType) for tier in al):
            raise ValueError('announce-list tier is not list')

    metainfo_result['nodes'] = validate_torrent_nodes(metainfo_result)
    metainfo_result['initial peers'] = validate_init_peers(metainfo)
    metainfo_result['url-list'] = validate_url_list(metainfo)
    metainfo_result['httpseeds'] = validate_http_seeds(metainfo)
    metainfo_result['info'] = validate_torrent_info(metainfo)

    # remove elements if None i.e. not valid.
    for key in {'httpseeds', 'url-list', 'nodes', 'initial peers'}:
        if not metainfo[key]:
            del metainfo[key]

    if not ('announce' in metainfo or 'nodes' in metainfo):
        # disabling this check, modifying metainfo to allow for ill-formatted torrents
        metainfo_result['nodes'] = []

    return dict((key, val) for key, val in metainfo_result.iteritems()
                if val or (metainfo[key] and metainfo[key] == val))