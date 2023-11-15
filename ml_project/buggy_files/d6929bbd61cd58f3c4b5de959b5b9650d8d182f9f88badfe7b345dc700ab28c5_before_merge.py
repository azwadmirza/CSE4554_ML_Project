    def schema(cls, by_alias=True) -> Dict[str, Any]:
        cached = cls._schema_cache.get(by_alias)
        if cached is not None:
            return cached

        s = {
            'type': 'object',
            'title': cls.__config__.title or cls.__name__,
        }
        if cls.__doc__:
            s['description'] = clean_docstring(cls.__doc__)

        if by_alias:
            s['properties'] = {f.alias: f.schema(by_alias) for f in cls.__fields__.values()}
        else:
            s['properties'] = {k: f.schema(by_alias) for k, f in cls.__fields__.items()}

        cls._schema_cache[by_alias] = s
        return s