    def can_create(cls, interpreter):
        if interpreter.has_venv:
            return Meta(can_symlink=fs_supports_symlink(), can_copy=True)
        return None