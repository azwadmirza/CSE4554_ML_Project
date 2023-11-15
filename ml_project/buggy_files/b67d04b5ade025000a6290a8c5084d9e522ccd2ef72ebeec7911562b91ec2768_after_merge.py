    def _resolve_pyvenv_canonical_python_binary(
        cls,
        real_binary,  # type: str
        maybe_venv_python_binary,  # type: str
    ):
        # type: (...) -> Optional[str]
        maybe_venv_python_binary = os.path.abspath(maybe_venv_python_binary)
        if not os.path.islink(maybe_venv_python_binary):
            return None

        pyvenv_cfg = cls._find_pyvenv_cfg(maybe_venv_python_binary)
        if pyvenv_cfg is None:
            return None

        while os.path.islink(maybe_venv_python_binary):
            resolved = os.readlink(maybe_venv_python_binary)
            if not os.path.isabs(resolved):
                resolved = os.path.abspath(
                    os.path.join(os.path.dirname(maybe_venv_python_binary), resolved)
                )
            if os.path.dirname(resolved) == os.path.dirname(maybe_venv_python_binary):
                maybe_venv_python_binary = resolved
            else:
                # We've escaped the venv bin dir; so the last resolved link was the
                # canonical venv Python binary.
                #
                # For example, for:
                #   ./venv/bin/
                #     python -> python3.8
                #     python3 -> python3.8
                #     python3.8 -> /usr/bin/python3.8
                #
                # We want to resolve each of ./venv/bin/python{,3{,.8}} to the canonical
                # ./venv/bin/python3.8 which is the symlink that points to the home binary.
                break
        return maybe_venv_python_binary