def _pydantic_post_init(self: 'DataclassType', *initvars: Any) -> None:
    if self.__post_init_original__:
        self.__post_init_original__(*initvars)
    d = validate_model(self.__pydantic_model__, self.__dict__, cls=self.__class__)[0]
    object.__setattr__(self, '__dict__', d)
    object.__setattr__(self, '__initialised__', True)
    if self.__post_init_post_parse__:
        self.__post_init_post_parse__()