    def __init__(
        self,
        binary,  # type: str
        prefix,  # type: str
        base_prefix,  # type: str
        python_tag,  # type: str
        abi_tag,  # type: str
        platform_tag,  # type: str
        version,  # type: Iterable[int]
        supported_tags,  # type: Iterable[tags.Tag]
        env_markers,  # type: Dict[str, str]
    ):
        # type: (...) -> None
        # N.B.: We keep this mapping to support historical values for `distribution` and `requirement`
        # properties.
        self._interpreter_name = self._find_interpreter_name(python_tag)

        self._binary = binary
        self._prefix = prefix
        self._base_prefix = base_prefix
        self._python_tag = python_tag
        self._abi_tag = abi_tag
        self._platform_tag = platform_tag
        self._version = tuple(version)
        self._supported_tags = tuple(supported_tags)
        self._env_markers = dict(env_markers)