        def needs_update(want, have, x):
            if isinstance(want.get(x), list) and isinstance(have.get(x), list):
                return want.get(x) and (want.get(x) != have.get(x)) and not all(elem in have.get(x) for elem in want.get(x))
            return want.get(x) and (want.get(x) != have.get(x))