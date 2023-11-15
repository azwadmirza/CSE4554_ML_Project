    def create_model(self, fields: Dict[str, Any], takes_args: bool, takes_kwargs: bool, config: 'ConfigType') -> None:
        pos_args = len(self.arg_mapping)

        class CustomConfig:
            pass

        if not TYPE_CHECKING:  # pragma: no branch
            if isinstance(config, dict):
                CustomConfig = type('Config', (), config)  # noqa: F811
            elif config is not None:
                CustomConfig = config  # noqa: F811

        if hasattr(CustomConfig, 'fields') or hasattr(CustomConfig, 'alias_generator'):
            raise ConfigError(
                'Setting the "fields" and "alias_generator" property on custom Config for '
                '@validate_arguments is not yet supported, please remove.'
            )

        class DecoratorBaseModel(BaseModel):
            @validator(self.v_args_name, check_fields=False, allow_reuse=True)
            def check_args(cls, v: List[Any]) -> List[Any]:
                if takes_args:
                    return v

                raise TypeError(f'{pos_args} positional arguments expected but {pos_args + len(v)} given')

            @validator(self.v_kwargs_name, check_fields=False, allow_reuse=True)
            def check_kwargs(cls, v: Dict[str, Any]) -> Dict[str, Any]:
                if takes_kwargs:
                    return v

                plural = '' if len(v) == 1 else 's'
                keys = ', '.join(map(repr, v.keys()))
                raise TypeError(f'unexpected keyword argument{plural}: {keys}')

            @validator(V_POSITIONAL_ONLY_NAME, check_fields=False, allow_reuse=True)
            def check_positional_only(cls, v: List[str]) -> None:
                plural = '' if len(v) == 1 else 's'
                keys = ', '.join(map(repr, v))
                raise TypeError(f'positional-only argument{plural} passed as keyword argument{plural}: {keys}')

            @validator(V_DUPLICATE_KWARGS, check_fields=False, allow_reuse=True)
            def check_duplicate_kwargs(cls, v: List[str]) -> None:
                plural = '' if len(v) == 1 else 's'
                keys = ', '.join(map(repr, v))
                raise TypeError(f'multiple values for argument{plural}: {keys}')

            class Config(CustomConfig):
                extra = Extra.forbid

        self.model = create_model(to_camel(self.raw_function.__name__), __base__=DecoratorBaseModel, **fields)