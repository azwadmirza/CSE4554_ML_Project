def _get_win_applications():
    """Return all system installed windows applications."""
    import winreg

    # See:
    # https://docs.microsoft.com/en-us/windows/desktop/shell/app-registration
    key_path = 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths'

    # Hive and flags
    hfs = [
        (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY),
        (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY),
        (winreg.HKEY_CURRENT_USER, 0),
    ]
    subkeys = [None]
    sort_key = 'key'
    app_paths = {}
    _apps = [_get_win_reg_info(key_path, hf[0], hf[1], subkeys) for hf in hfs]
    software_list = itertools.chain(*_apps)
    for software in sorted(software_list, key=lambda x: x[sort_key]):
        if software[None]:
            key = software['key'].capitalize().replace('.exe', '')
            expanded_fpath = os.path.expandvars(software[None]).lower()
            if '"' in expanded_fpath or "'" in expanded_fpath:
                expanded_fpath = literal_eval(expanded_fpath)
            app_paths[key] = expanded_fpath

    # See:
    # https://www.blog.pythonlibrary.org/2010/03/03/finding-installed-software-using-python/
    # https://stackoverflow.com/q/53132434
    key_path = 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall'
    subkeys = ['DisplayName', 'InstallLocation', 'DisplayIcon']
    sort_key = 'DisplayName'
    apps = {}
    _apps = [_get_win_reg_info(key_path, hf[0], hf[1], subkeys) for hf in hfs]
    software_list = itertools.chain(*_apps)
    for software in sorted(software_list, key=lambda x: x[sort_key]):
        location = software['InstallLocation']
        name = software['DisplayName']
        icon = software['DisplayIcon']
        key = software['key']
        if name and icon:
            icon = icon.replace('"', '').replace("'", '')
            icon = icon.split(',')[0]

            if location == '' and icon:
                location = os.path.dirname(icon)

            if not os.path.isfile(icon):
                icon = ''

            if location and os.path.isdir(location):
                files = [f for f in os.listdir(location)
                         if os.path.isfile(os.path.join(location, f))]
                if files:
                    for fname in files:
                        fn_low = fname.lower()
                        valid_file = fn_low.endswith(('.exe', '.com', '.bat'))
                        if valid_file and not fn_low.startswith('unins'):
                            fpath = os.path.join(location, fname)
                            expanded_fpath = os.path.expandvars(fpath.lower())
                            if '"' in expanded_fpath or "'" in expanded_fpath:
                                expanded_fpath = literal_eval(expanded_fpath)
                            apps[name + ' (' + fname + ')'] = expanded_fpath
    # Join data
    values = list(zip(*apps.values()))[-1]
    for name, fpath in app_paths.items():
        if fpath not in values:
            apps[name] = fpath

    return apps