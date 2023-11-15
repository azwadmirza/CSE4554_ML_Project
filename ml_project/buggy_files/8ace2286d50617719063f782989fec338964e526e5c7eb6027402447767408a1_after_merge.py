    def get_cmap(klass, name):
        if name == 'Identity-H':
            return IdentityCMap(WMode=0)
        elif name == 'Identity-V':
            return IdentityCMap(WMode=1)
        elif name == 'OneByteIdentityH':
            return IdentityCMapByte(WMode=0)
        elif name == 'OneByteIdentityV':
            return IdentityCMapByte(WMode=1)
        try:
            return klass._cmap_cache[name]
        except KeyError:
            pass
        data = klass._load_data(name)
        klass._cmap_cache[name] = cmap = PyCMap(name, data)
        return cmap