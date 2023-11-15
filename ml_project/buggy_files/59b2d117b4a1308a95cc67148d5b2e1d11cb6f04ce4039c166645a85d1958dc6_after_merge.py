def create_extension_list(patterns, exclude=None, ctx=None, aliases=None, quiet=False, language=None,
                          exclude_failures=False):
    if language is not None:
        print('Please put "# distutils: language=%s" in your .pyx or .pxd file(s)' % language)
    if exclude is None:
        exclude = []
    if patterns is None:
        return [], {}
    elif isinstance(patterns, basestring) or not isinstance(patterns, collections.Iterable):
        patterns = [patterns]
    explicit_modules = set([m.name for m in patterns if isinstance(m, Extension)])
    seen = set()
    deps = create_dependency_tree(ctx, quiet=quiet)
    to_exclude = set()
    if not isinstance(exclude, list):
        exclude = [exclude]
    for pattern in exclude:
        to_exclude.update(map(os.path.abspath, extended_iglob(pattern)))

    module_list = []
    module_metadata = {}

    # workaround for setuptools
    if 'setuptools' in sys.modules:
        Extension_distutils = sys.modules['setuptools.extension']._Extension
        Extension_setuptools = sys.modules['setuptools'].Extension
    else:
        # dummy class, in case we do not have setuptools
        Extension_distutils = Extension
        class Extension_setuptools(Extension): pass

    # if no create_extension() function is defined, use a simple
    # default function.
    create_extension = ctx.options.create_extension or default_create_extension

    for pattern in patterns:
        if isinstance(pattern, str):
            filepattern = pattern
            template = Extension(pattern, [])  # Fake Extension without sources
            name = '*'
            base = None
            ext_language = language
        elif isinstance(pattern, (Extension_distutils, Extension_setuptools)):
            cython_sources = [s for s in pattern.sources
                              if os.path.splitext(s)[1] in ('.py', '.pyx')]
            if cython_sources:
              filepattern = cython_sources[0]
              if len(cython_sources) > 1:
                print("Warning: Multiple cython sources found for extension '%s': %s\n"
                "See http://cython.readthedocs.io/en/latest/src/userguide/sharing_declarations.html "
                "for sharing declarations among Cython files." % (pattern.name, cython_sources))
            else:
                # ignore non-cython modules
                module_list.append(pattern)
                continue
            template = pattern
            name = template.name
            base = DistutilsInfo(exn=template)
            ext_language = None  # do not override whatever the Extension says
        else:
            msg = str("pattern is not of type str nor subclass of Extension (%s)"
                      " but of type %s and class %s" % (repr(Extension),
                                                        type(pattern),
                                                        pattern.__class__))
            raise TypeError(msg)

        for file in nonempty(sorted(extended_iglob(filepattern)), "'%s' doesn't match any files" % filepattern):
            if os.path.abspath(file) in to_exclude:
                continue
            pkg = deps.package(file)
            module_name = deps.fully_qualified_name(file)
            if '*' in name:
                if module_name in explicit_modules:
                    continue
            elif name != module_name:
                print("Warning: Extension name '%s' does not match fully qualified name '%s' of '%s'" % (
                    name, module_name, file))
                module_name = name

            if module_name not in seen:
                try:
                    kwds = deps.distutils_info(file, aliases, base).values
                except Exception:
                    if exclude_failures:
                        continue
                    raise
                if base is not None:
                    for key, value in base.values.items():
                        if key not in kwds:
                            kwds[key] = value

                kwds['name'] = module_name

                sources = [file] + [m for m in template.sources if m != filepattern]
                if 'sources' in kwds:
                    # allow users to add .c files etc.
                    for source in kwds['sources']:
                        source = encode_filename_in_py2(source)
                        if source not in sources:
                            sources.append(source)
                kwds['sources'] = sources

                if ext_language and 'language' not in kwds:
                    kwds['language'] = ext_language

                np_pythran = kwds.pop('np_pythran', False)

                # Create the new extension
                m, metadata = create_extension(template, kwds)
                m.np_pythran = np_pythran or getattr(m, 'np_pythran', False)
                if m.np_pythran:
                    update_pythran_extension(m)
                module_list.append(m)

                # Store metadata (this will be written as JSON in the
                # generated C file but otherwise has no purpose)
                module_metadata[module_name] = metadata

                if file not in m.sources:
                    # Old setuptools unconditionally replaces .pyx with .c/.cpp
                    target_file = os.path.splitext(file)[0] + ('.cpp' if m.language == 'c++' else '.c')
                    try:
                        m.sources.remove(target_file)
                    except ValueError:
                        # never seen this in the wild, but probably better to warn about this unexpected case
                        print("Warning: Cython source file not found in sources list, adding %s" % file)
                    m.sources.insert(0, file)
                seen.add(name)
    return module_list, module_metadata