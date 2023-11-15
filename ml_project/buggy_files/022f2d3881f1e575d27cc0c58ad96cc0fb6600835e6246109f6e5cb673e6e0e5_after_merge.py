def get_color_scheme(name):
    """Get syntax color scheme"""
    color_scheme = {}
    for key in sh.COLOR_SCHEME_KEYS:
        color_scheme[key] = CONF.get(
            "appearance",
            "%s/%s" % (name, key),
            default=sh.COLOR_SCHEME_DEFAULT_VALUES[key])
    return color_scheme