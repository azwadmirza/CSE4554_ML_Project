def recursive_finder(name, data, py_module_names, py_module_cache, zf):
    """
    Using ModuleDepFinder, make sure we have all of the module_utils files that
    the module its module_utils files needs.
    """
    # Parse the module and find the imports of ansible.module_utils
    try:
        tree = ast.parse(data)
    except (SyntaxError, IndentationError) as e:
        raise AnsibleError("Unable to import %s due to %s" % (name, e.msg))
    finder = ModuleDepFinder()
    finder.visit(tree)

    #
    # Determine what imports that we've found are modules (vs class, function.
    # variable names) for packages
    #

    normalized_modules = set()
    # Loop through the imports that we've found to normalize them
    # Exclude paths that match with paths we've already processed
    # (Have to exclude them a second time once the paths are processed)

    module_utils_paths = [p for p in module_utils_loader._get_paths(subdirs=False) if os.path.isdir(p)]
    module_utils_paths.append(_MODULE_UTILS_PATH)
    for py_module_name in finder.submodules.difference(py_module_names):
        module_info = None

        if py_module_name[0] == 'six':
            # Special case the python six library because it messes up the
            # import process in an incompatible way
            module_info = imp.find_module('six', module_utils_paths)
            py_module_name = ('six',)
            idx = 0
        elif py_module_name[0] == '_six':
            # Special case the python six library because it messes up the
            # import process in an incompatible way
            module_info = imp.find_module('_six', [os.path.join(p, 'six') for p in module_utils_paths])
            py_module_name = ('six', '_six')
            idx = 0
        else:
            # Check whether either the last or the second to last identifier is
            # a module name
            for idx in (1, 2):
                if len(py_module_name) < idx:
                    break
                try:
                    module_info = imp.find_module(py_module_name[-idx],
                                                  [os.path.join(p, *py_module_name[:-idx]) for p in module_utils_paths])
                    break
                except ImportError:
                    continue

        # Could not find the module.  Construct a helpful error message.
        if module_info is None:
            msg = ['Could not find imported module support code for %s.  Looked for' % (name,)]
            if idx == 2:
                msg.append('either %s.py or %s.py' % (py_module_name[-1], py_module_name[-2]))
            else:
                msg.append(py_module_name[-1])
            raise AnsibleError(' '.join(msg))

        # Found a byte compiled file rather than source.  We cannot send byte
        # compiled over the wire as the python version might be different.
        # imp.find_module seems to prefer to return source packages so we just
        # error out if imp.find_module returns byte compiled files (This is
        # fragile as it depends on undocumented imp.find_module behaviour)
        if module_info[2][2] not in (imp.PY_SOURCE, imp.PKG_DIRECTORY):
            msg = ['Could not find python source for imported module support code for %s.  Looked for' % name]
            if idx == 2:
                msg.append('either %s.py or %s.py' % (py_module_name[-1], py_module_name[-2]))
            else:
                msg.append(py_module_name[-1])
            raise AnsibleError(' '.join(msg))

        if idx == 2:
            # We've determined that the last portion was an identifier and
            # thus, not part of the module name
            py_module_name = py_module_name[:-1]

        # If not already processed then we've got work to do
        # If not in the cache, then read the file into the cache
        # We already have a file handle for the module open so it makes
        # sense to read it now
        if py_module_name not in py_module_cache:
            if module_info[2][2] == imp.PKG_DIRECTORY:
                # Read the __init__.py instead of the module file as this is
                # a python package
                normalized_name = py_module_name + ('__init__',)
                if normalized_name not in py_module_names:
                    normalized_path = os.path.join(os.path.join(module_info[1], '__init__.py'))
                    normalized_data = _slurp(normalized_path)
                    py_module_cache[normalized_name] = (normalized_data, normalized_path)
                    normalized_modules.add(normalized_name)
            else:
                normalized_name = py_module_name
                if normalized_name not in py_module_names:
                    normalized_path = module_info[1]
                    normalized_data = module_info[0].read()
                    module_info[0].close()
                    py_module_cache[normalized_name] = (normalized_data, normalized_path)
                    normalized_modules.add(normalized_name)

            # Make sure that all the packages that this module is a part of
            # are also added
            for i in range(1, len(py_module_name)):
                py_pkg_name = py_module_name[:-i] + ('__init__',)
                if py_pkg_name not in py_module_names:
                    pkg_dir_info = imp.find_module(py_pkg_name[-1],
                                                   [os.path.join(p, *py_pkg_name[:-1]) for p in module_utils_paths])
                    normalized_modules.add(py_pkg_name)
                    py_module_cache[py_pkg_name] = (_slurp(pkg_dir_info[1]), pkg_dir_info[1])

    # FIXME: Currently the AnsiBallZ wrapper monkeypatches module args into a global
    # variable in basic.py.  If a module doesn't import basic.py, then the AnsiBallZ wrapper will
    # traceback when it tries to monkypatch.  So, for now, we have to unconditionally include
    # basic.py.
    #
    # In the future we need to change the wrapper to monkeypatch the args into a global variable in
    # their own, separate python module.  That way we won't require basic.py.  Modules which don't
    # want basic.py can import that instead.  AnsibleModule will need to change to import the vars
    # from the separate python module and mirror the args into its global variable for backwards
    # compatibility.
    if ('basic',) not in py_module_names:
        pkg_dir_info = imp.find_module('basic', module_utils_paths)
        normalized_modules.add(('basic',))
        py_module_cache[('basic',)] = (_slurp(pkg_dir_info[1]), pkg_dir_info[1])
    # End of AnsiballZ hack

    #
    # iterate through all of the ansible.module_utils* imports that we haven't
    # already checked for new imports
    #

    # set of modules that we haven't added to the zipfile
    unprocessed_py_module_names = normalized_modules.difference(py_module_names)

    for py_module_name in unprocessed_py_module_names:
        py_module_path = os.path.join(*py_module_name)
        py_module_file_name = '%s.py' % py_module_path

        zf.writestr(os.path.join("ansible/module_utils",
                    py_module_file_name), py_module_cache[py_module_name][0])
        display.vvvvv("Using module_utils file %s" % py_module_cache[py_module_name][1])

    # Add the names of the files we're scheduling to examine in the loop to
    # py_module_names so that we don't re-examine them in the next pass
    # through recursive_finder()
    py_module_names.update(unprocessed_py_module_names)

    for py_module_file in unprocessed_py_module_names:
        recursive_finder(py_module_file, py_module_cache[py_module_file][0], py_module_names, py_module_cache, zf)
        # Save memory; the file won't have to be read again for this ansible module.
        del py_module_cache[py_module_file]