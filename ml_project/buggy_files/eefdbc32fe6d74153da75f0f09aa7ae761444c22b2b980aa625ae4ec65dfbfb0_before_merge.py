    def __init__(
        self, binary, python_tag, abi_tag, platform_tag, version, supported_tags, env_markers
    ):
        # N.B.: We keep this mapping to support historical values for `distribution` and `requirement`
        # properties.
        self._interpreter_name = self._find_interpreter_name(python_tag)

        self._binary = binary
        self._python_tag = python_tag
        self._abi_tag = abi_tag
        self._platform_tag = platform_tag
        self._version = tuple(version)
        self._supported_tags = tuple(supported_tags)
        self._env_markers = dict(env_markers)