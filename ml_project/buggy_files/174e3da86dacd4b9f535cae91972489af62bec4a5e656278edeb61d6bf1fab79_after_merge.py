                def impl(a, sep=None, maxsplit=-1):
                    return _map_bytes(a._to_str().split(maxsplit=maxsplit))