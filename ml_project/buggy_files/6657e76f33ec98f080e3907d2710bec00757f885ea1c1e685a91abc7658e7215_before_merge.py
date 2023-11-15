def tdef_to_metadata_dict(tdef):
    """
    Helper function to create a TorrentMetadata-compatible dict from TorrentDef
    """
    # We only want to determine the type of the data. XXX filtering is done by the receiving side
    tags = default_category_filter.calculateCategory(tdef.metainfo, tdef.get_name_as_unicode())

    return {
        "infohash": tdef.get_infohash(),
        "title": tdef.get_name_as_unicode()[:300],  # TODO: do proper size checking based on bytes
        "tags": tags[:200],  # TODO: do proper size checking based on bytes
        "size": tdef.get_length(),
        "torrent_date": datetime.fromtimestamp(tdef.get_creation_date()),
        "tracker_info": get_uniformed_tracker_url(tdef.get_tracker() or '') or ''}