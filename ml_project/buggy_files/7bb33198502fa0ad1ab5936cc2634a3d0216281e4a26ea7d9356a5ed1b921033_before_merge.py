    def __init__(self, value: Any, items: Union['AbstractSetIntStr', 'MappingIntStrAny']) -> None:
        if TYPE_CHECKING:
            self._items: Union['AbstractSetIntStr', 'MappingIntStrAny']
            self._type: Type[Union[set, dict]]  # type: ignore

        # For further type checks speed-up
        if isinstance(items, dict):
            self._type = dict
        elif isinstance(items, AbstractSet):
            self._type = set
        else:
            raise TypeError(f'Unexpected type of exclude value {items.__class__}')

        if isinstance(value, (list, tuple)):
            try:
                items = self._normalize_indexes(items, len(value))
            except TypeError as e:
                raise TypeError(
                    'Excluding fields from a sequence of sub-models or dicts must be performed index-wise: '
                    'expected integer keys or keyword "__all__"'
                ) from e

        self._items = items