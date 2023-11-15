def _getScriptSettingsFromIniFile(policy_info):
    '''
    helper function to parse/read a GPO Startup/Shutdown script file

    psscript.ini and script.ini file definitions are here
        https://msdn.microsoft.com/en-us/library/ff842529.aspx
        https://msdn.microsoft.com/en-us/library/dd303238.aspx
    '''
    _existingData = None
    if os.path.isfile(policy_info['ScriptIni']['IniPath']):
        with salt.utils.fopen(policy_info['ScriptIni']['IniPath'], 'rb') as fhr:
            _existingData = fhr.read()
        if _existingData:
            try:
                _existingData = deserialize(_existingData.decode('utf-16-le').lstrip('\ufeff'))
                log.debug('Have deserialized data {0}'.format(_existingData))
            except Exception as error:
                log.error('An error occurred attempting to deserialize data for {0}'.format(policy_info['Policy']))
                raise CommandExecutionError(error)
            if 'Section' in policy_info['ScriptIni'] and policy_info['ScriptIni']['Section'].lower() in [z.lower() for z in _existingData.keys()]:
                if 'SettingName' in policy_info['ScriptIni']:
                    log.debug('Need to look for {0}'.format(policy_info['ScriptIni']['SettingName']))
                    if policy_info['ScriptIni']['SettingName'].lower() in [z.lower() for z in _existingData[policy_info['ScriptIni']['Section']].keys()]:
                        return _existingData[policy_info['ScriptIni']['Section']][policy_info['ScriptIni']['SettingName'].lower()]
                    else:
                        return None
                else:
                    return _existingData[policy_info['ScriptIni']['Section']]
            else:
                return None

    return None