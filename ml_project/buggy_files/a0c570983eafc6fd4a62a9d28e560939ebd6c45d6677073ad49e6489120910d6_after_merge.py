    def can_create(cls, interpreter):
        """By default all built-in methods assume that if we can describe it we can create it"""
        # first we must be able to describe it
        if cls.can_describe(interpreter):
            meta = cls.setup_meta(interpreter)
            if meta is not None and meta:
                for src in cls.sources(interpreter):
                    if src.exists:
                        if meta.can_copy and not src.can_copy:
                            meta.copy_error = "cannot copy {}".format(src)
                        if meta.can_symlink and not src.can_symlink:
                            meta.symlink_error = "cannot symlink {}".format(src)
                        if not meta.can_copy and not meta.can_symlink:
                            meta.error = "neither copy or symlink supported: {}".format(
                                meta.copy_error, meta.symlink_error
                            )
                    else:
                        meta.error = "missing required file {}".format(src)
                    if meta.error:
                        break
                    meta.sources.append(src)
            return meta
        return None