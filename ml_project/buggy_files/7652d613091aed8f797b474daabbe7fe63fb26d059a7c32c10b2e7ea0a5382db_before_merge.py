def get_rc_urls():
    if rc.get('channels') is None:
        return []
    if 'system' in rc['channels']:
        raise RuntimeError("system cannot be used in .condarc")
    return rc['channels']