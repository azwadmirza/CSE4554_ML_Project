def options_absent(name, sections=None, separator='='):
    '''
    .. code-block:: yaml

        /home/saltminion/api-paste.ini:
          ini.options_absent:
            - separator: '='
            - sections:
                test:
                  - testkey
                  - secondoption
                test1:
                  - testkey1

    options present in file and not specified in sections
    dict will be untouched

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
            except AttributeError:
                cur_section = section
            if isinstance(sections[section], (dict, OrderedDict)):
                for key in sections[section]:
                    cur_value = cur_section.get(key)
                    if not cur_value:
                        ret['comment'] += 'Key {0}{1} does not exist.\n'.format(key, section_name)
                        continue
                    ret['comment'] += 'Deleted key {0}{1}.\n'.format(key, section_name)
                    ret['result'] = None
            else:
                option = section
                if not __salt__['ini.get_option'](name, None, option, separator):
                    ret['comment'] += 'Key {0} does not exist.\n'.format(option)
                    continue
                ret['comment'] += 'Deleted key {0}.\n'.format(option)
                ret['result'] = None

        if ret['comment'] == '':
            ret['comment'] = 'No changes detected.'
        return ret
    sections = sections or {}
    for section, keys in six.iteritems(sections):
        for key in keys:
            try:
                current_value = __salt__['ini.remove_option'](name, section, key, separator)
            except IOError as err:
                ret['comment'] = "{0}".format(err)
                ret['result'] = False
                return ret
            if not current_value:
                continue
            if section not in ret['changes']:
                ret['changes'].update({section: {}})
            ret['changes'][section].update({key: current_value})
            if not isinstance(sections[section], (dict, OrderedDict)):
                ret['changes'].update({section: current_value})
                # break
            ret['comment'] = 'Changes take effect'
    return ret