def should_transcode(item, fmt):
    """Determine whether the item should be transcoded as part of
    conversion (i.e., its bitrate is high or it has the wrong format).
    """
    if config['convert']['never_convert_lossy_files'] and \
            not (item.format.lower() in LOSSLESS_FORMATS):
        return False
    maxbr = config['convert']['max_bitrate'].get(int)
    return fmt.lower() != item.format.lower() or \
        item.bitrate >= 1000 * maxbr