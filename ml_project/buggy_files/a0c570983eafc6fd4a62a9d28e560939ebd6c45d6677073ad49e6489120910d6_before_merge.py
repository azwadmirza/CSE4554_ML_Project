    def can_create(cls, interpreter):
        """By default all built-in methods assume that if we can describe it we can create it"""
        # first we must be able to describe it
        if cls.can_describe(interpreter):
            sources = []
            can_copy = True
            can_symlink = fs_supports_symlink()
            for src in cls.sources(interpreter):
                if src.exists:
                    if can_copy and not src.can_copy:
                        can_copy = False
                        logging.debug("%s cannot copy %s", cls.__name__, src)
                    if can_symlink and not src.can_symlink:
                        can_symlink = False
                        logging.debug("%s cannot symlink %s", cls.__name__, src)
                    if not (can_copy or can_symlink):
                        break
                else:
                    logging.debug("%s missing %s", cls.__name__, src)
                    break
                sources.append(src)
            else:
                return Meta(sources, can_copy, can_symlink)
        return None