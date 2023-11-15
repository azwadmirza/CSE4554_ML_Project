def check_modules(project, match, root=None):
    """Verify that only vendored modules have been imported."""
    if root is None:
        root = project_root(project)
    extensions = []
    unvendored = {}
    for modname, mod in list(sys.modules.items()):
        if not match(modname, mod):
            continue
        if not hasattr(mod, '__file__'):  # extension module
            extensions.append(modname)
        elif not mod.__file__.startswith(root):
            unvendored[modname] = mod.__file__
    return unvendored, extensions