    def can_create(cls, interpreter):
        if interpreter.has_venv:
            meta = ViaGlobalRefMeta()
            if interpreter.platform == "win32" and interpreter.version_info.major == 3:
                meta = handle_store_python(meta, interpreter)
            return meta
        return None