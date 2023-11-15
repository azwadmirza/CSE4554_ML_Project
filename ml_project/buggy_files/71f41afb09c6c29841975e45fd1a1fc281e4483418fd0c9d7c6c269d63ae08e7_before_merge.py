    def __init__(
        self,
        keys: Iterable[str],
        desc: str,
        env_name: Optional[str],
        of_type: Type[T],
        default: Union[Callable[["Config", Optional[str]], T], T],
        post_process: Optional[Callable[[T, "Config"], T]] = None,
    ) -> None:
        super().__init__(keys, desc, env_name)
        self.of_type = of_type
        self.default = default
        self.post_process = post_process
        self._cache: Union[object, T] = _PLACE_HOLDER