    def schema(cls, by_alias=True) -> Dict[str, Any]:
        cached = cls._schema_cache.get(by_alias)
        if cached is not None:
            return cached
        s = {'title': cls.__config__.title or cls.__name__}
        if cls.__doc__:
            s['description'] = clean_docstring(cls.__doc__)

        s.update(cls.type_schema(by_alias))
        cls._schema_cache[by_alias] = s
        return s