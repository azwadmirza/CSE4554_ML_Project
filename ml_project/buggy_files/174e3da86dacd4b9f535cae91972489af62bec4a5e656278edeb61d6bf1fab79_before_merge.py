                def impl(a, maxsplit=-1):
                    return _map_bytes(a._to_str().split(maxsplit=maxsplit))