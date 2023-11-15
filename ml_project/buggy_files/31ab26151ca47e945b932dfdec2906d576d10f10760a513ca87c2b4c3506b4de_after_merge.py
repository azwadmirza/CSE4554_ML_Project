    def __init__(self, *args: Any, box_settings: Any = None, default_box: bool = False, default_box_attr: Any = NO_DEFAULT,
                 default_box_none_transform: bool = True, frozen_box: bool = False, camel_killer_box: bool = False,
                 conversion_box: bool = True, modify_tuples_box: bool = False, box_safe_prefix: str = 'x',
                 box_duplicates: str = 'ignore', box_intact_types: Union[Tuple, List] = (),
                 box_recast: Dict = None, box_dots: bool = False, **kwargs: Any):
        super().__init__()
        self._box_config = _get_box_config()
        self._box_config.update({
            'default_box': default_box,
            'default_box_attr': self.__class__ if default_box_attr is NO_DEFAULT else default_box_attr,
            'default_box_none_transform': default_box_none_transform,
            'conversion_box': conversion_box,
            'box_safe_prefix': box_safe_prefix,
            'frozen_box': frozen_box,
            'camel_killer_box': camel_killer_box,
            'modify_tuples_box': modify_tuples_box,
            'box_duplicates': box_duplicates,
            'box_intact_types': tuple(box_intact_types),
            'box_recast': box_recast,
            'box_dots': box_dots,
            'box_settings': box_settings or {}
        })
        if not self._box_config['conversion_box'] and self._box_config['box_duplicates'] != 'ignore':
            raise BoxError('box_duplicates are only for conversion_boxes')
        if len(args) == 1:
            if isinstance(args[0], str):
                raise BoxValueError('Cannot extrapolate Box from string')
            if isinstance(args[0], Mapping):
                for k, v in args[0].items():
                    if v is args[0]:
                        v = self

                    if v is None and self._box_config['default_box'] and self._box_config['default_box_none_transform']:
                        continue
                    self.__setitem__(k, v)
            elif isinstance(args[0], Iterable):
                for k, v in args[0]:
                    self.__setitem__(k, v)
            else:
                raise BoxValueError('First argument must be mapping or iterable')
        elif args:
            raise BoxTypeError(f'Box expected at most 1 argument, got {len(args)}')

        for k, v in kwargs.items():
            if args and isinstance(args[0], Mapping) and v is args[0]:
                v = self
            self.__setitem__(k, v)

        self._box_config['__created'] = True