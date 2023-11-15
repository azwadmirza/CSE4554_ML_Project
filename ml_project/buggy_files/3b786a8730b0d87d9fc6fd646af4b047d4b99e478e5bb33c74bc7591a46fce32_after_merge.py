def options_present(name, sections=None, separator='=', strict=False):
    '''
    .. code-block:: yaml

        /home/saltminion/api-paste.ini:
          ini.options_present:
            - separator: '='
            - strict: True
            - sections:
                test:
                  testkey: 'testval'
                  secondoption: 'secondvalue'
                test1:
                  testkey1: 'testval121'

    options present in file and not specified in sections
    dict will be untouched, unless `strict: True` flag is
    used

    changes dict will contain the list of changes made
    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'No anomaly detected'
           }
    if __opts__['test']:
        ret['comment'] = ''
    # pylint: disable=too-many-nested-blocks
    try:
        changes = {}
        if sections:
            options = {}
            for sname, sbody in sections.items():
                if not isinstance(sbody, (dict, OrderedDict)):
                    options.update({sname: sbody})
            cur_ini = __salt__['ini.get_ini'](name, separator)
            original_top_level_opts = {}
            original_sections = {}
            for key, val in cur_ini.items():
                if isinstance(val, (dict, OrderedDict)):
                    original_sections.update({key: val})
                else:
                    original_top_level_opts.update({key: val})
            if __opts__['test']:
                for option in options:
                    if option in original_top_level_opts:
                        if six.text_type(original_top_level_opts[option]) == six.text_type(options[option]):
                            ret['comment'] += 'Unchanged key {0}.\n'.format(option)
                        else:
                            ret['comment'] += 'Changed key {0}.\n'.format(option)
                            ret['result'] = None
                    else:
                        ret['comment'] += 'Changed key {0}.\n'.format(option)
                        ret['result'] = None
            else:
                options_updated = __salt__['ini.set_option'](name, options, separator)
                changes.update(options_updated)
            if strict:
                for opt_to_remove in set(original_top_level_opts).difference(options):
                    if __opts__['test']:
                        ret['comment'] += 'Removed key {0}.\n'.format(opt_to_remove)
                        ret['result'] = None
                    else:
                        __salt__['ini.remove_option'](name, None, opt_to_remove, separator)
                        changes.update({opt_to_remove: {'before': original_top_level_opts[opt_to_remove],
                                                        'after': None}})
            for section_name, section_body in [(sname, sbody) for sname, sbody in sections.items()
                                               if isinstance(sbody, (dict, OrderedDict))]:
                changes[section_name] = {}
                if strict:
                    original = cur_ini.get(section_name, {})
                    for key_to_remove in set(original.keys()).difference(section_body.keys()):
                        orig_value = original_sections.get(section_name, {}).get(key_to_remove, '#-#-')
                        if __opts__['test']:
                            ret['comment'] += 'Deleted key {0} in section {1}.\n'.format(key_to_remove, section_name)
                            ret['result'] = None
                        else:
                            __salt__['ini.remove_option'](name, section_name, key_to_remove, separator)
                            changes[section_name].update({key_to_remove: ''})
                            changes[section_name].update({key_to_remove: {'before': orig_value,
                                                                          'after': None}})
                if __opts__['test']:
                    for option in section_body:
                        if six.text_type(section_body[option]) == \
                                six.text_type(original_sections.get(section_name, {}).get(option, '#-#-')):
                            ret['comment'] += 'Unchanged key {0} in section {1}.\n'.format(option, section_name)
                        else:
                            ret['comment'] += 'Changed key {0} in section {1}.\n'.format(option, section_name)
                            ret['result'] = None
                else:
                    options_updated = __salt__['ini.set_option'](name, {section_name: section_body}, separator)
                    if options_updated:
                        changes[section_name].update(options_updated[section_name])
                    if not changes[section_name]:
                        del changes[section_name]
        else:
            if not __opts__['test']:
                changes = __salt__['ini.set_option'](name, sections, separator)
    except (IOError, KeyError) as err:
        ret['comment'] = "{0}".format(err)
        ret['result'] = False
        return ret
    if 'error' in changes:
        ret['result'] = False
        ret['comment'] = 'Errors encountered. {0}'.format(changes['error'])
        ret['changes'] = {}
    else:
        for ciname, body in changes.items():
            if body:
                ret['comment'] = 'Changes take effect'
                ret['changes'].update({ciname: changes[ciname]})
    return ret