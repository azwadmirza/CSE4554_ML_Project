def __init__(opts):
    salt.utils.compat.pack_dunder(__name__)
    if HAS_LIBCLOUD:
        __utils__['libcloud.assign_funcs'](__name__, 'dns', pack=__salt__)