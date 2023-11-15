def loadhandlers(path, global_conf=None, **kwargs):
    loader = ConfigLoader(path)
    handlers = {}
    handlers.update(
        (name[8:], loadhandler(loader, name[8:], global_conf, **kwargs))
        for name in loader.get_sections(prefix="handler")
    )
    return handlers