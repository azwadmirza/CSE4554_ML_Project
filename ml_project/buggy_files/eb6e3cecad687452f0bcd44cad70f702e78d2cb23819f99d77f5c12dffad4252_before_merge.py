def iter_packaging_files(project):
    """Yield the filenames for all files in the project.

    The filenames are relative to "debugpy/_vendored".  This is most
    useful for the "package data" in a setup.py.
    """
    # TODO: Use default filters?  __pycache__ and .pyc?
    prune_dir = None
    exclude_file = None
    try:
        mod = import_module('._{}_packaging'.format(project), __name__)
    except ImportError:
        pass
    else:
        prune_dir = getattr(mod, 'prune_dir', prune_dir)
        exclude_file = getattr(mod, 'exclude_file', exclude_file)
    results = iter_project_files(
        project,
        relative=True,
        prune_dir=prune_dir,
        exclude_file=exclude_file,
    )
    for _, _, filename in results:
        yield filename