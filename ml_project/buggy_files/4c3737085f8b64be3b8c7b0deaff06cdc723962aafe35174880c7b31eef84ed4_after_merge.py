            def join_list_impl(sep, parts):
                _parts = [str(p) for p in parts]
                return join_list(sep, _parts)