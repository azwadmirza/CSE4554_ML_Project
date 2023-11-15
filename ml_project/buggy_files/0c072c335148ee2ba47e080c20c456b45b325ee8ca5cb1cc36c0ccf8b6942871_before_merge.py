    def __new__(cls, *args: Any,  box_settings: Any, default_box: bool = False, default_box_attr: Any = NO_DEFAULT,
                default_box_none_transform: bool = True, frozen_box: bool = False, camel_killer_box: bool = False,
                conversion_box: bool = True, modify_tuples_box: bool = False, box_safe_prefix: str = 'x',
                box_duplicates: str = 'ignore', box_intact_types: Union[Tuple, List] = (),
                box_recast: Dict = None, box_dots: bool = False, **kwargs: Any):
        """
        Due to the way pickling works in python 3, we need to make sure
        the box config is created as early as possible.
        """
        obj = super(Box, cls).__new__(cls, *args, **kwargs)
        obj._box_config = _get_box_config()
        obj._box_config.update({
            'default_box': default_box,
            'default_box_attr': cls.__class__ if default_box_attr is NO_DEFAULT else default_box_attr,
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
            'box_settings': box_settings
        })
        return obj