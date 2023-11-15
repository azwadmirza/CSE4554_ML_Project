        def get_stash(m):
            id = m.group(1)
            if id in stash:
                return stash.get(id)