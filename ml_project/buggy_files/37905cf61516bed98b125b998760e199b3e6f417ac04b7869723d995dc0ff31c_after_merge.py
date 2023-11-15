    def encode(self):
        values = dict(
            binary=self._binary,
            prefix=self._prefix,
            base_prefix=self._base_prefix,
            python_tag=self._python_tag,
            abi_tag=self._abi_tag,
            platform_tag=self._platform_tag,
            version=self._version,
            supported_tags=[
                (tag.interpreter, tag.abi, tag.platform) for tag in self._supported_tags
            ],
            env_markers=self._env_markers,
        )
        return json.dumps(values, sort_keys=True)