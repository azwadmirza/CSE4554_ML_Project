    def _to_typing(self, raw: T, of_type: Type[V], kwargs: Mapping[str, Any]) -> V:
        origin = getattr(of_type, "__origin__", of_type.__class__)
        result: Any = _NO_MAPPING
        if origin in (list, List):
            entry_type = of_type.__args__[0]  # type: ignore[attr-defined]
            result = [self.to(i, entry_type, kwargs) for i in self.to_list(raw, entry_type)]
        elif origin in (set, Set):
            entry_type = of_type.__args__[0]  # type: ignore[attr-defined]
            result = {self.to(i, entry_type, kwargs) for i in self.to_set(raw, entry_type)}
        elif origin in (dict, Dict):
            key_type, value_type = of_type.__args__[0], of_type.__args__[1]  # type: ignore[attr-defined]
            result = OrderedDict(
                (self.to(k, key_type, {}), self.to(v, value_type, {}))
                for k, v in self.to_dict(raw, (key_type, value_type))
            )
        elif origin == Union:  # handle Optional values
            args: List[Type[Any]] = of_type.__args__  # type: ignore[attr-defined]
            none = type(None)
            if len(args) == 2 and none in args:
                if isinstance(raw, str):
                    raw = raw.strip()  # type: ignore[assignment]
                if not raw:
                    result = None
                else:
                    new_type = next(i for i in args if i != none)  # pragma: no cover # this will always find a element
                    result = self.to(raw, new_type, kwargs)
        elif origin == Literal or origin == type(Literal):
            if sys.version_info >= (3, 7):  # pragma: no cover (py37+)
                choice = of_type.__args__
            else:  # pragma: no cover (py38+)
                choice = of_type.__values__  # type: ignore[attr-defined]
            if raw not in choice:
                raise ValueError(f"{raw} must be one of {choice}")
            result = raw
        if result is not _NO_MAPPING:
            return cast(V, result)
        raise TypeError(f"{raw} cannot cast to {of_type!r}")