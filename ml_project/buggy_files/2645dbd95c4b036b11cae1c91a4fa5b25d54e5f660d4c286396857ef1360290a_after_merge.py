def sections_absent(name, sections=None, separator='='):
    '''
    .. code-block:: yaml

        /home/saltminion/api-paste.ini:
          ini.sections_absent:
            - separator: '='
            - sections:
                - test
                - test1

    options present in file and not specified in sections will be deleted
    changes dict will contain the sections that changed
    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'No anomaly detected'
           }
    if __opts__['test']:
        ret['result'] = True
        ret['comment'] = ''
        try:
            cur_ini = __salt__['ini.get_ini'](name, separator)
        except IOError as err:
            ret['result'] = False
            ret['comment'] = "{0}".format(err)
            return ret
        for section in sections or []:
            if section not in cur_ini:
                ret['comment'] += 'Section {0} does not exist.\n'.format(section)
                continue
            ret['comment'] += 'Deleted section {0}.\n'.format(section)
            ret['result'] = None
        if ret['comment'] == '':
            ret['comment'] = 'No changes detected.'
        return ret
    for section in sections or []:
        try:
            cur_section = __salt__['ini.remove_section'](name, section, separator)
        except IOError as err:
            ret['result'] = False
            ret['comment'] = "{0}".format(err)
            return ret
        if not cur_section:
            continue
        ret['changes'][section] = cur_section
        ret['comment'] = 'Changes take effect'
    return ret