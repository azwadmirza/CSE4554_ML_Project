def _getScriptSettingsFromIniFile(policy_info):
    '''
    helper function to parse/read a GPO Startup/Shutdown script file
    '''
    _existingData = _read_regpol_file(policy_info['ScriptIni']['IniPath'])
    if _existingData:
        _existingData = _existingData.split('\r\n')
        script_settings = {}
        this_section = None
        for eLine in _existingData:
            if eLine.startswith('[') and eLine.endswith(']'):
                this_section = eLine.replace('[', '').replace(']', '')
                log.debug('adding section {0}'.format(this_section))
                if this_section:
                    script_settings[this_section] = {}
            else:
                if '=' in eLine:
                    log.debug('working with config line {0}'.format(eLine))
                    eLine = eLine.split('=')
                    if this_section in script_settings:
                        script_settings[this_section][eLine[0]] = eLine[1]
        if 'SettingName' in policy_info['ScriptIni']:
            log.debug('Setting Name is in policy_info')
            if policy_info['ScriptIni']['SettingName'] in script_settings[policy_info['ScriptIni']['Section']]:
                log.debug('the value is set in the file')
                return script_settings[policy_info['ScriptIni']['Section']][policy_info['ScriptIni']['SettingName']]
            else:
                return None
        elif policy_info['ScriptIni']['Section'] in script_settings:
            log.debug('no setting name')
            return script_settings[policy_info['ScriptIni']['Section']]
        else:
            log.debug('broad else')
            return None
    return None