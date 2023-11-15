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
        ret['result'] = True
        ret['comment'] = ''
        for section in sections or {}:
            section_name = ' in section ' + section if section != 'DEFAULT_IMPLICIT' else ''
            try:
                cur_section = __salt__['ini.get_section'](name, section, separator)
            except IOError as err:
                ret['comment'] = "{0}".format(err)
                ret['result'] = False
                return ret
            for key in sections[section]:
                cur_value = cur_section.get(key)
                if cur_value == six.text_type(sections[section][key]):
                    ret['comment'] += 'Key {0}{1} unchanged.\n'.format(key, section_name)
                    continue
                ret['comment'] += 'Changed key {0}{1}.\n'.format(key, section_name)
                ret['result'] = None
        if ret['comment'] == '':
            ret['comment'] = 'No changes detected.'
        return ret
    try:
        changes = {}
        if sections:
            for section_name, section_body in sections.items():
                changes[section_name] = {}
                if strict:
                    original = __salt__['ini.get_section'](name, section_name, separator)
                    for key_to_remove in set(original.keys()).difference(section_body.keys()):
                        orig_value = __salt__['ini.get_option'](name, section_name, key_to_remove, separator)
                        __salt__['ini.remove_option'](name, section_name, key_to_remove, separator)
                        changes[section_name].update({key_to_remove: ''})
                        changes[section_name].update({key_to_remove: {'before': orig_value,
                                                                      'after': None}})
                options_updated = __salt__['ini.set_option'](name, {section_name: section_body}, separator)
                if options_updated:
                    changes[section_name].update(options_updated[section_name])
                if not changes[section_name]:
                    del changes[section_name]
        else:
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
        for name, body in changes.items():
            if body:
                ret['comment'] = 'Changes take effect'
                ret['changes'].update({name: changes[name]})
    return ret