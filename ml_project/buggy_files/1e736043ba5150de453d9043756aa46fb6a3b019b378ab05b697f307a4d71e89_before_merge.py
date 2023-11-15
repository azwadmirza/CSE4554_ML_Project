def render(template, saltenv='base', sls='', salt_data=True, **kwargs):
    if 'pyobjects_states' not in __context__:
        load_states()

    # these hold the scope that our sls file will be executed with
    _locals = {}
    _globals = {}

    # create our StateFactory objects
    mod_globals = {'StateFactory': StateFactory}
    for mod in __context__['pyobjects_states']:
        mod_locals = {}
        mod_camel = ''.join([
            part.capitalize()
            for part in mod.split('_')
        ])
        valid_funcs = "','".join(
            __context__['pyobjects_states'][mod]
        )
        mod_cmd = "{0} = StateFactory('{1!s}', valid_funcs=['{2}'])".format(
            mod_camel,
            mod,
            valid_funcs
        )
        exec_(mod_cmd, mod_globals, mod_locals)

        _globals[mod_camel] = mod_locals[mod_camel]

    # add our include and extend functions
    _globals['include'] = Registry.include
    _globals['extend'] = Registry.make_extend

    # add our map class
    Map.__salt__ = __salt__
    _globals['Map'] = Map

    # add some convenience methods to the global scope as well as the "dunder"
    # format of all of the salt objects
    try:
        _globals.update({
            # salt, pillar & grains all provide shortcuts or object interfaces
            'salt': SaltObject(__salt__),
            'pillar': __salt__['pillar.get'],
            'grains': __salt__['grains.get'],
            'mine': __salt__['mine.get'],
            'config': __salt__['config.get'],

            # the "dunder" formats are still available for direct use
            '__salt__': __salt__,
            '__pillar__': __pillar__,
            '__grains__': __grains__
        })
    except NameError:
        pass

    # if salt_data is not True then we just return the global scope we've
    # built instead of returning salt data from the registry
    if not salt_data:
        return _globals

    # this will be used to fetch any import files
    client = get_file_client(__opts__)

    # process our sls imports
    #
    # we allow pyobjects users to use a special form of the import statement
    # so that they may bring in objects from other files. while we do this we
    # disable the registry since all we're looking for here is python objects,
    # not salt state data
    template_data = []
    Registry.enabled = False
    for line in template.readlines():
        line = line.rstrip('\r\n')
        matched = False
        for RE in (IMPORT_RE, FROM_RE):
            matches = re.match(RE, line)
            if not matches:
                continue

            import_file = matches.group(1).strip()
            try:
                imports = matches.group(2).split(',')
            except IndexError:
                # if we don't have a third group in the matches object it means
                # that we're importing everything
                imports = None

            state_file = client.cache_file(import_file, saltenv)
            if not state_file:
                raise ImportError("Could not find the file {0!r}".format(import_file))

            with salt.utils.fopen(state_file) as f:
                state_contents = f.read()

            state_locals = {}
            exec_(state_contents, _globals, state_locals)

            if imports is None:
                imports = list(state_locals.keys())

            for name in imports:
                name = alias = name.strip()

                matches = re.match(FROM_AS_RE, name)
                if matches is not None:
                    name = matches.group(1).strip()
                    alias = matches.group(2).strip()

                if name not in state_locals:
                    raise ImportError("{0!r} was not found in {1!r}".format(
                        name,
                        import_file
                    ))
                _globals[alias] = state_locals[name]

            matched = True
            break

        if not matched:
            template_data.append(line)

    final_template = "\n".join(template_data)

    # re-enable the registry
    Registry.enabled = True

    # now exec our template using our created scopes
    exec_(final_template, _globals, _locals)

    return Registry.salt_data()