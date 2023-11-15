    def _pydantic_post_init(self: 'DataclassType', *initvars: Any) -> None:
        if post_init_original is not None:
            post_init_original(self, *initvars)
        d = validate_model(self.__pydantic_model__, self.__dict__, cls=self.__class__)[0]
        object.__setattr__(self, '__dict__', d)
        object.__setattr__(self, '__initialised__', True)
        if post_init_post_parse is not None:
            post_init_post_parse(self)