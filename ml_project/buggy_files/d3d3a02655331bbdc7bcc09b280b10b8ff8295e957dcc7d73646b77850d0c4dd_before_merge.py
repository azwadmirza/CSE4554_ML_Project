def render(yaml_data, saltenv='base', sls='', argline='', **kws):
    '''
    Accepts YAML as a string or as a file object and runs it through the YAML
    parser.

    :rtype: A Python data structure
    '''
    if not isinstance(yaml_data, string_types):
        yaml_data = yaml_data.read()
    with warnings.catch_warnings(record=True) as warn_list:
        try:
            data = load(yaml_data, Loader=get_yaml_loader(argline))
        except ScannerError as exc:
            err_type = _ERROR_MAP.get(exc.problem, exc.problem)
            line_num = exc.problem_mark.line + 1
            raise SaltRenderError(err_type, line_num, exc.problem_mark.buffer)
        except ConstructorError as exc:
            raise SaltRenderError(exc)
        if len(warn_list) > 0:
            for item in warn_list:
                log.warning(
                    '{warn} found in {sls} saltenv={env}'.format(
                        warn=item.message, sls=salt.utils.url.create(sls), env=saltenv
                    )
                )
        if not data:
            data = {}
        else:
            if 'config.get' in __salt__:
                if __salt__['config.get']('yaml_utf8', False):
                    data = _yaml_result_unicode_to_utf8(data)
            elif __opts__.get('yaml_utf8'):
                data = _yaml_result_unicode_to_utf8(data)
        log.debug('Results of YAML rendering: \n{0}'.format(data))

        def _validate_data(data):
            '''
            PyYAML will for some reason allow improper YAML to be formed into
            an unhashable dict (that is, one with a dict as a key). This
            function will recursively go through and check the keys to make
            sure they're not dicts.
            '''
            if isinstance(data, dict):
                for key, value in six.iteritems(data):
                    if isinstance(key, dict):
                        raise SaltRenderError(
                            'Invalid YAML, possible double curly-brace')
                    _validate_data(value)
            elif isinstance(data, list):
                for item in data:
                    _validate_data(item)

        _validate_data(data)
        return data