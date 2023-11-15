def run_module(mod_name):
    from hy.importer import MetaImporter
    pth = MetaImporter().find_on_path(mod_name)
    if pth is not None:
        sys.argv = [pth] + sys.argv
        return run_file(pth)

    sys.stderr.write("{0}: module '{1}' not found.\n".format(hy.__appname__,
                                                             mod_name))
    return 1