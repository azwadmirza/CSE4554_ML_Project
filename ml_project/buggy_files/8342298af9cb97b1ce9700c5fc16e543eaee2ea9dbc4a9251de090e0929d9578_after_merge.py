def execute_config(args, parser):
    json_warnings = []
    json_get = {}

    if args.show_sources:
        if context.json:
            print(json.dumps(context.collect_all(), sort_keys=True,
                             indent=2, separators=(',', ': ')))
        else:
            lines = []
            for source, reprs in iteritems(context.collect_all()):
                lines.append("==> %s <==" % source)
                lines.extend(format_dict(reprs))
                lines.append('')
            print('\n'.join(lines))
        return

    if args.show:
        from collections import OrderedDict

        d = OrderedDict((key, getattr(context, key))
                        for key in context.list_parameters())
        if context.json:
            print(json.dumps(d, sort_keys=True, indent=2, separators=(',', ': '),
                  cls=EntityEncoder))
        else:
            # coerce channels
            d['custom_channels'] = {k: text_type(v).replace(k, '')  # TODO: the replace here isn't quite right  # NOQA
                                    for k, v in iteritems(d['custom_channels'])}
            # TODO: custom_multichannels needs better formatting
            d['custom_multichannels'] = {k: json.dumps([text_type(c) for c in chnls])
                                         for k, chnls in iteritems(d['custom_multichannels'])}

            print('\n'.join(format_dict(d)))
        context.validate_configuration()
        return

    if args.describe:
        paramater_names = context.list_parameters()
        if context.json:
            print(json.dumps([context.describe_parameter(name) for name in paramater_names],
                             sort_keys=True, indent=2, separators=(',', ': '),
                             cls=EntityEncoder))
        else:
            def clean_element_type(element_types):
                _types = set()
                for et in element_types:
                    _types.add('str') if isinstance(et, string_types) else _types.add('%s' % et)
                return tuple(sorted(_types))

            for name in paramater_names:
                details = context.describe_parameter(name)
                aliases = details['aliases']
                string_delimiter = details.get('string_delimiter')
                element_types = details['element_types']
                if details['parameter_type'] == 'primitive':
                    print("%s (%s)" % (name, ', '.join(clean_element_type(element_types))))
                else:
                    print("%s (%s: %s)" % (name, details['parameter_type'],
                                           ', '.join(clean_element_type(element_types))))
                def_str = '  default: %s' % json.dumps(details['default_value'], indent=2,
                                                       separators=(',', ': '),
                                                       cls=EntityEncoder)
                print('\n  '.join(def_str.split('\n')))
                if aliases:
                    print("  aliases: %s" % ', '.join(aliases))
                if string_delimiter:
                    print("  string delimiter: '%s'" % string_delimiter)
                print('\n  '.join(wrap('  ' + details['description'], 70)))
                print()
        return

    if args.validate:
        context.validate_all()
        return

    if args.system:
        rc_path = sys_rc_path
    elif args.env:
        if 'CONDA_PREFIX' in os.environ:
            rc_path = join(os.environ['CONDA_PREFIX'], '.condarc')
        else:
            rc_path = user_rc_path
    elif args.file:
        rc_path = args.file
    else:
        rc_path = user_rc_path

    # read existing condarc
    if os.path.exists(rc_path):
        with open(rc_path, 'r') as fh:
            rc_config = yaml_load(fh) or {}
    else:
        rc_config = {}

    # Get
    if args.get is not None:
        context.validate_all()
        if args.get == []:
            args.get = sorted(rc_config.keys())
        for key in args.get:
            if key not in rc_list_keys + rc_bool_keys + rc_string_keys:
                if key not in rc_other:
                    message = "unknown key %s" % key
                    if not context.json:
                        print(message, file=sys.stderr)
                    else:
                        json_warnings.append(message)
                continue
            if key not in rc_config:
                continue

            if context.json:
                json_get[key] = rc_config[key]
                continue

            if isinstance(rc_config[key], (bool, string_types)):
                print("--set", key, rc_config[key])
            else:  # assume the key is a list-type
                # Note, since conda config --add prepends, these are printed in
                # the reverse order so that entering them in this order will
                # recreate the same file
                items = rc_config.get(key, [])
                numitems = len(items)
                for q, item in enumerate(reversed(items)):
                    # Use repr so that it can be pasted back in to conda config --add
                    if key == "channels" and q in (0, numitems-1):
                        print("--add", key, repr(item),
                              "  # lowest priority" if q == 0 else "  # highest priority")
                    else:
                        print("--add", key, repr(item))

    # prepend, append, add
    for arg, prepend in zip((args.prepend, args.append), (True, False)):
        sequence_parameters = [p for p in context.list_parameters()
                               if context.describe_parameter(p)['parameter_type'] == 'sequence']
        for key, item in arg:
            if key == 'channels' and key not in rc_config:
                rc_config[key] = ['defaults']
            if key not in sequence_parameters:
                raise CondaValueError("Key '%s' is not a known sequence parameter." % key)
            if not isinstance(rc_config.get(key, []), list):
                bad = rc_config[key].__class__.__name__
                raise CouldntParseError("key %r should be a list, not %s." % (key, bad))
            if key == 'default_channels' and rc_path != sys_rc_path:
                msg = "'default_channels' is only configurable for system installs"
                raise NotImplementedError(msg)
            arglist = rc_config.setdefault(key, [])
            if item in arglist:
                # Right now, all list keys should not contain duplicates
                message = "Warning: '%s' already in '%s' list, moving to the %s" % (
                    item, key, "top" if prepend else "bottom")
                arglist = rc_config[key] = [p for p in arglist if p != item]
                if not context.json:
                    print(message, file=sys.stderr)
                else:
                    json_warnings.append(message)
            arglist.insert(0 if prepend else len(arglist), item)

    # Set
    for key, item in args.set:
        primitive_parameters = [p for p in context.list_parameters()
                                if context.describe_parameter(p)['parameter_type'] == 'primitive']
        if key not in primitive_parameters:
            raise CondaValueError("Key '%s' is not a known primitive parameter." % key)
        value = context.typify_parameter(key, item)
        rc_config[key] = value

    # Remove
    for key, item in args.remove:
        if key not in rc_config:
            if key != 'channels':
                raise CondaKeyError(key, "key %r is not in the config file" % key)
            rc_config[key] = ['defaults']
        if item not in rc_config[key]:
            raise CondaKeyError(key, "%r is not in the %r key of the config file" %
                                (item, key))
        rc_config[key] = [i for i in rc_config[key] if i != item]

    # Remove Key
    for key, in args.remove_key:
        if key not in rc_config:
            raise CondaKeyError(key, "key %r is not in the config file" %
                                key)
        del rc_config[key]

    # config.rc_keys
    if not args.get:
        try:
            with open(rc_path, 'w') as rc:
                rc.write(yaml_dump(rc_config))
        except (IOError, OSError) as e:
            raise CondaError('Cannot write to condarc file at %s\n'
                             'Caused by %r' % (rc_path, e))

    if context.json:
        stdout_json_success(
            rc_path=rc_path,
            warnings=json_warnings,
            get=json_get
        )
    return