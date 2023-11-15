def export_to_dictionary(target, whitelist, dic, fullcopy=True):
    """ Exports attributes of target from whitelist.keys() to dictionary dic
    All values are references only by default.

    Parameters
    ----------
        target : object
            must contain the (nested) attributes of the whitelist.keys()
        whitelist : dictionary
            A dictionary, keys of which are used as attributes for exporting.
            Key 'self' is only available with tag 'id', when the id of the
            target is saved. The values are either None, or a tuple, where:
                - the first item a string, which containts flags, separated by
                commas.
                - the second item is None if no 'init' flag is given, otherwise
                the object required for the initialization.
            The flag conventions are as follows:
            * 'init':
                object used for initialization of the target. The object is
                saved in the tuple in whitelist
            * 'fn':
                the targeted attribute is a function, and may be pickled. A
                tuple of (thing, value) will be exported to the dictionary,
                where thing is None if function is passed as-is, and True if
                dill package is used to pickle the function, with the value as
                the result of the pickle.
            * 'id':
                the id of the targeted attribute is exported (e.g.
                id(target.name))
            * 'sig':
                The targeted attribute is a signal, and will be converted to a
                dictionary if fullcopy=True
        dic : dictionary
            A dictionary where the object will be exported
        fullcopy : bool
            Copies of objects are stored, not references. If any found,
            functions will be pickled and signals converted to dictionaries

    """
    whitelist_flags = {}
    for key, value in whitelist.items():
        if value is None:
            # No flags and/or values are given, just save the target
            thing = attrgetter(key)(target)
            if fullcopy:
                thing = deepcopy(thing)
            dic[key] = thing
            whitelist_flags[key] = ''
            continue

        flags_str, value = value
        flags = parse_flag_string(flags_str)
        check_that_flags_make_sense(flags)
        if key is 'self':
            if 'id' not in flags:
                raise ValueError(
                    'Key "self" is only available with flag "id" given')
            value = id(target)
        else:
            if 'id' in flags:
                value = id(attrgetter(key)(target))

        # here value is either id(thing), or None (all others except 'init'),
        # or something for init
        if 'init' not in flags and value is None:
            value = attrgetter(key)(target)
        # here value either id(thing), or an actual target to export
        if 'sig' in flags:
            if fullcopy:
                from hyperspy.signal import Signal
                if isinstance(value, Signal):
                    value = value._to_dictionary()
                    value['data'] = deepcopy(value['data'])
        elif 'fn' in flags:
            if fullcopy:
                value = (True, dill.dumps(value))
            else:
                value = (None, value)
        elif fullcopy:
            value = deepcopy(value)

        dic[key] = value
        whitelist_flags[key] = flags_str

    if '_whitelist' not in dic:
        dic['_whitelist'] = {}
    # the saved whitelist does not have any values, as they are saved in the
    # original dictionary. Have to restore then when loading from dictionary,
    # most notably all with 'init' flags!!
    dic['_whitelist'].update(whitelist_flags)