def sections_present(name, sections=None, separator='='):
    '''
    .. code-block:: yaml

        /home/saltminion/api-paste.ini:
          ini.sections_present:
            - separator: '='
            - sections:
                - section_one
                - section_two

    This will only create empty sections. To also create options, use
    options_present state

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
        for section in sections or {}:
            try:
                cur_section = __salt__['ini.get_section'](name, section, separator)
            except IOError as err:
                ret['result'] = False
                ret['comment'] = "{0}".format(err)
                return ret
            if dict(sections[section]) == cur_section:
                ret['comment'] += 'Section unchanged {0}.\n'.format(section)
                continue
            elif cur_section:
                ret['comment'] += 'Changed existing section {0}.\n'.format(section)
            else:
                ret['comment'] += 'Created new section {0}.\n'.format(section)
            ret['result'] = None
        if ret['comment'] == '':
            ret['comment'] = 'No changes detected.'
        return ret
    section_to_update = {}
    for section_name in sections or []:
        section_to_update.update({section_name: {}})
    try:
        changes = __salt__['ini.set_option'](name, section_to_update, separator)
    except IOError as err:
        ret['result'] = False
        ret['comment'] = "{0}".format(err)
        return ret
    if 'error' in changes:
        ret['result'] = False
        ret['changes'] = 'Errors encountered {0}'.format(changes['error'])
        return ret
    ret['changes'] = changes
    ret['comment'] = 'Changes take effect'
    return ret