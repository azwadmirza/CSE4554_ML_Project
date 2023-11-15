def prepend(name,
            text=None,
            makedirs=False,
            source=None,
            source_hash=None,
            template='jinja',
            sources=None,
            source_hashes=None,
            defaults=None,
            context=None):
    '''
    Ensure that some text appears at the beginning of a file

    The text will not be prepended again if it already exists in the file. You
    may specify a single line of text or a list of lines to append.

    Multi-line example:

    .. code-block:: yaml

        /etc/motd:
          file.prepend:
            - text: |
                Thou hadst better eat salt with the Philosophers of Greece,
                than sugar with the Courtiers of Italy.
                - Benjamin Franklin

    Multiple lines of text:

    .. code-block:: yaml

        /etc/motd:
          file.prepend:
            - text:
              - Trust no one unless you have eaten much salt with him.
              - "Salt is born of the purest of parents: the sun and the sea."

    Gather text from multiple template files:

    .. code-block:: yaml

        /etc/motd:
          file:
              - prepend
              - template: jinja
              - sources:
                  - salt://motd/devops-messages.tmpl
                  - salt://motd/hr-messages.tmpl
                  - salt://motd/general-messages.tmpl

    .. versionadded:: 2014.7.0
    '''
    ret = {'name': name, 'changes': {}, 'result': False, 'comment': ''}
    if not name:
        return _error(ret, 'Must provide name to file.prepend')

    if sources is None:
        sources = []

    if source_hashes is None:
        source_hashes = []

    # Add sources and source_hashes with template support
    # NOTE: FIX 'text' and any 'source' are mutually exclusive as 'text'
    #       is re-assigned in the original code.
    (ok_, err, sl_) = _unify_sources_and_hashes(source=source,
                                                source_hash=source_hash,
                                                sources=sources,
                                                source_hashes=source_hashes)
    if not ok_:
        return _error(ret, err)

    if makedirs is True:
        dirname = os.path.dirname(name)
        if not __salt__['file.directory_exists'](dirname):
            __salt__['file.makedirs'](name)
            check_res, check_msg = _check_directory(
                dirname, None, None, False, None, False, False, None
            )
            if not check_res:
                return _error(ret, check_msg)

        # Make sure that we have a file
        __salt__['file.touch'](name)

    check_res, check_msg = _check_file(name)
    if not check_res:
        return _error(ret, check_msg)

    #Follow the original logic and re-assign 'text' if using source(s)...
    if sl_:
        tmpret = _get_template_texts(source_list=sl_,
                                     template=template,
                                     defaults=defaults,
                                     context=context)
        if not tmpret['result']:
            return tmpret
        text = tmpret['data']

    if isinstance(text, string_types):
        text = (text,)

    with salt.utils.fopen(name, 'rb') as fp_:
        slines = fp_.readlines()

    count = 0
    test_lines = []

    preface = []
    for chunk in text:

        if __salt__['file.contains_regex_multiline'](
                name, salt.utils.build_whitespace_split_regex(chunk)):
            continue

        try:
            lines = chunk.splitlines()
        except AttributeError:
            log.debug(
                'Error appending text to {0}; given object is: {1}'.format(
                    name, type(chunk)
                )
            )
            return _error(ret, 'Given text is not a string')

        for line in lines:
            if __opts__['test']:
                ret['comment'] = 'File {0} is set to be updated'.format(name)
                ret['result'] = None
                test_lines.append('{0}\n'.format(line))
            else:
                preface.append(line)
            count += 1

    if __opts__['test']:
        nlines = test_lines + slines
        if slines != nlines:
            if not salt.utils.istextfile(name):
                ret['changes']['diff'] = 'Replace binary file'
            else:
                # Changes happened, add them
                ret['changes']['diff'] = (
                    ''.join(difflib.unified_diff(slines, nlines))
                )
            ret['result'] = None
        else:
            ret['comment'] = 'File {0} is in correct state'.format(name)
            ret['result'] = True
        return ret

    __salt__['file.prepend'](name, *preface)

    with salt.utils.fopen(name, 'rb') as fp_:
        nlines = fp_.readlines()

    if slines != nlines:
        if not salt.utils.istextfile(name):
            ret['changes']['diff'] = 'Replace binary file'
        else:
            # Changes happened, add them
            ret['changes']['diff'] = (
                ''.join(difflib.unified_diff(slines, nlines))
            )

    if count:
        ret['comment'] = 'Prepended {0} lines'.format(count)
    else:
        ret['comment'] = 'File {0} is in correct state'.format(name)
    ret['result'] = True
    return ret