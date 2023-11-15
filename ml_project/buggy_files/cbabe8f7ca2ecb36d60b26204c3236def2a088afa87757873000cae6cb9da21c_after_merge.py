def audit(data_list, tags, labels, debug=False, **kwargs):
    '''
    Runs secedit on the local machine and audits the return data
    with the CIS yaml processed by __virtual__
    '''
    __data__ = {}
    __secdata__ = _secedit_export()
    __sidaccounts__ = _get_account_sid()
    for profile, data in data_list:
        _merge_yaml(__data__, data, profile)
    __data__ = apply_labels(__data__, labels)
    __tags__ = _get_tags(__data__)
    if debug:
        log.debug('secedit audit __data__:')
        log.debug(__data__)
        log.debug('secedit audit __tags__:')
        log.debug(__tags__)

    ret = {'Success': [], 'Failure': [], 'Controlled': []}
    for tag in __tags__:
        if fnmatch.fnmatch(tag, tags):
            for tag_data in __tags__[tag]:
                if 'control' in tag_data:
                    ret['Controlled'].append(tag_data)
                    continue
                name = tag_data['name']
                audit_type = tag_data['type']
                output = tag_data['match_output'].lower()

                # Blacklisted audit (do not include)
                if audit_type == 'blacklist':
                    if 'no one' in output:
                        if name not in __secdata__:
                            ret['Success'].append(tag_data)
                        else:
                            tag_data['failure_reason'] = "No value/account should be configured " \
                                                         "under '{0}', but atleast one value/account" \
                                                         " is configured on the system.".format(name)
                            ret['Failure'].append(tag_data)
                    else:
                        if name in __secdata__:
                            secret = _translate_value_type(__secdata__[name], tag_data['value_type'], tag_data['match_output'])
                            if secret:
                                tag_data['failure_reason'] = "Value of the key '{0}' is configured to a " \
                                                             "blacklisted value '{1}({2})'" \
                                                             .format(name,
                                                                     tag_data['match_output'],
                                                                     tag_data['value_type'])
                                ret['Failure'].append(tag_data)
                            else:
                                ret['Success'].append(tag_data)

                # Whitelisted audit (must include)
                if audit_type == 'whitelist':
                    if name in __secdata__:
                        sec_value = __secdata__[name]
                        tag_data['found_value'] = sec_value
                        if 'MACHINE\\' in name:
                            match_output = _reg_value_translator(tag_data['match_output'])
                        else:
                            match_output = tag_data['match_output']
                        if ',' in sec_value and '\\' in sec_value:
                            sec_value = sec_value.split(',')
                            match_output = match_output.split(',')
                        if 'account' in tag_data['value_type']:
                            secret = _translate_value_type(sec_value, tag_data['value_type'], match_output, __sidaccounts__)
                        else:
                            secret = _translate_value_type(sec_value, tag_data['value_type'], match_output)
                        if secret:
                            ret['Success'].append(tag_data)
                        else:
                            tag_data['failure_reason'] = "Value of the key '{0}' is configured to" \
                                                         " invalid value '{1}'. It should be set to" \
                                                         " '{2}({3})'".format(name,
                                                                             sec_value,
                                                                             match_output,
                                                                             tag_data['value_type'])
                            ret['Failure'].append(tag_data)
                    else:
                        log.error('name {} was not in __secdata__'.format(name))
                        tag_data['failure_reason'] = "Value of the key '{0}' could not be found in" \
                                                     " the registry. It should be set to '{1}({2})'" \
                                                     .format(name,
                                                             tag_data['match_output'],
                                                             tag_data['value_type'])
                        ret['Failure'].append(tag_data)

    return ret