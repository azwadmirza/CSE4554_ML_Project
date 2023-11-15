def loadhandlers(path, names, global_conf=None, **kwargs):
    loader = ConfigLoader(path)
    handlers = {}
    handlers.update(
        (name, loadhandler(loader, name, global_conf, **kwargs))
        for name in names
    )
    return handlers