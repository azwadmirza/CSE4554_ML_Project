def _build_m3u_filename(basename):
    """Builds unique m3u filename by appending given basename to current
    date."""

    basename = re.sub(r"[\s,/\\'\"]", '_', basename)
    date = datetime.datetime.now().strftime("%Y%m%d_%Hh%M")
    path = normpath(os.path.join(
        config['importfeeds']['dir'].as_filename(),
        date + '_' + basename + '.m3u'
    ))
    return path