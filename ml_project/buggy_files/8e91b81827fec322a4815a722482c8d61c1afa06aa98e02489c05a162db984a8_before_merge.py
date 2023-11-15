def generate_autosummary_docs(sources: List[str], output_dir: str = None,
                              suffix: str = '.rst', warn: Callable = None,
                              info: Callable = None, base_path: str = None,
                              builder: Builder = None, template_dir: str = None,
                              imported_members: bool = False, app: Any = None,
                              overwrite: bool = True) -> None:
    if info:
        warnings.warn('info argument for generate_autosummary_docs() is deprecated.',
                      RemovedInSphinx40Warning)
        _info = info
    else:
        _info = logger.info

    if warn:
        warnings.warn('warn argument for generate_autosummary_docs() is deprecated.',
                      RemovedInSphinx40Warning)
        _warn = warn
    else:
        _warn = logger.warning

    showed_sources = list(sorted(sources))
    if len(showed_sources) > 20:
        showed_sources = showed_sources[:10] + ['...'] + showed_sources[-10:]
    _info(__('[autosummary] generating autosummary for: %s') %
          ', '.join(showed_sources))

    if output_dir:
        _info(__('[autosummary] writing to %s') % output_dir)

    if base_path is not None:
        sources = [os.path.join(base_path, filename) for filename in sources]

    template = AutosummaryRenderer(builder, template_dir)

    # read
    items = find_autosummary_in_files(sources)

    # keep track of new files
    new_files = []

    # write
    for entry in sorted(set(items), key=str):
        if entry.path is None:
            # The corresponding autosummary:: directive did not have
            # a :toctree: option
            continue

        path = output_dir or os.path.abspath(entry.path)
        ensuredir(path)

        try:
            name, obj, parent, mod_name = import_by_name(entry.name)
        except ImportError as e:
            _warn(__('[autosummary] failed to import %r: %s') % (entry.name, e))
            continue

        content = generate_autosummary_content(name, obj, parent, template, entry.template,
                                               imported_members, app, entry.recursive)

        filename = os.path.join(path, name + suffix)
        if os.path.isfile(filename):
            with open(filename) as f:
                old_content = f.read()

            if content == old_content:
                continue
            elif overwrite:  # content has changed
                with open(filename, 'w') as f:
                    f.write(content)
                new_files.append(filename)
        else:
            with open(filename, 'w') as f:
                f.write(content)
            new_files.append(filename)

    # descend recursively to new files
    if new_files:
        generate_autosummary_docs(new_files, output_dir=output_dir,
                                  suffix=suffix, warn=warn, info=info,
                                  base_path=base_path, builder=builder,
                                  template_dir=template_dir,
                                  imported_members=imported_members, app=app,
                                  overwrite=overwrite)