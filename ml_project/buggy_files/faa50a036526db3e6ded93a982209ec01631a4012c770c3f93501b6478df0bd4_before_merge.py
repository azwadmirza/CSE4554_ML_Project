def add_extensions(options):

    extensions = []
    for ext in options.extensions:
        if not ext.startswith('!'):
            extensions.append(ext)
            continue
        ext = ext[1:]
        try:
            extensions.remove(ext)
        except ValueError:
            log.warning(
                'Could not remove extension %s -- no such extension installed' % ext
            )
        else:
            log.info('Removed extension %s' % ext)

    options.extensions[:] = extensions
    if not extensions:
        return

    class ModuleProxy(object):
        def __init__(self):
            self.__dict__ = globals()

    createpdf = ModuleProxy()
    for modname in options.extensions:
        prefix, modname = os.path.split(modname)
        path_given = prefix
        if modname.endswith('.py'):
            modname = modname[:-3]
            path_given = True
        if not prefix:
            prefix = os.path.join(os.path.dirname(__file__), 'extensions')
            if prefix not in sys.path:
                sys.path.append(prefix)
            prefix = os.getcwd()
        if prefix not in sys.path:
            sys.path.insert(0, prefix)
        log.info('Importing extension module %s', repr(modname))
        firstname = path_given and modname or (modname + '_r2p')
        _names = [firstname, modname]
        try:
            for _name in _names:
                try:
                    module = import_module(_name, 'rst2pdf')
                except ImportError:
                    continue
        except ImportError as e:
            if str(e).split()[-1].replace("'", '') not in [firstname, modname]:
                raise
            raise SystemExit(
                '\nError: Could not find module %s '
                'in sys.path [\n    %s\n]\nExiting...\n'
                % (modname, ',\n    '.join(sys.path))
            )
        if hasattr(module, 'install'):
            module.install(createpdf, options)