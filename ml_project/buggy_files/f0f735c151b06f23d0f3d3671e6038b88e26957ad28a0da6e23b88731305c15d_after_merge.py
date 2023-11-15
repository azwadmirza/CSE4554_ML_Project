    def get(cls, binary=None):
        # type: (Optional[str]) -> PythonIdentity

        # N.B.: We should not need to look past `sys.executable` to learn the current interpreter's
        # executable path, but on OSX there has been a bug where the `sys.executable` reported is
        # _not_ the path of the current interpreter executable:
        #   https://bugs.python.org/issue22490#msg283859
        # That case is distinguished by the presence of a `__PYVENV_LAUNCHER__` environment
        # variable as detailed in the Python bug linked above.
        if binary and binary != sys.executable and "__PYVENV_LAUNCHER__" not in os.environ:
            # Here we assume sys.executable is accurate and binary is something like a pyenv shim.
            binary = sys.executable

        supported_tags = tuple(tags.sys_tags())
        preferred_tag = supported_tags[0]
        return cls(
            binary=binary or sys.executable,
            prefix=sys.prefix,
            base_prefix=(
                # Old virtualenv (16 series and lower) sets `sys.real_prefix` in all cases.
                getattr(sys, "real_prefix", None)
                # Both pyvenv and virtualenv 20+ set `sys.base_prefix` as per
                # https://www.python.org/dev/peps/pep-0405/.
                or getattr(sys, "base_prefix", sys.prefix)
            ),
            python_tag=preferred_tag.interpreter,
            abi_tag=preferred_tag.abi,
            platform_tag=preferred_tag.platform,
            version=sys.version_info[:3],
            supported_tags=supported_tags,
            env_markers=markers.default_environment(),
        )