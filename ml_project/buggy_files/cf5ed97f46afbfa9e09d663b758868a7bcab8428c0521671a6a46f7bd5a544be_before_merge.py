        def needs_update(want, have, x):
            return want.get(x) and (want.get(x) != have.get(x))