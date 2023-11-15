def _binary_analysis(app_dic):
    """Start binary analsis."""
    logger.info("Starting Binary Analysis")
    bin_an_dic = {}

    # Init optional sections to prevent None-Pointer-Errors
    bin_an_dic['results'] = []
    bin_an_dic['warnings'] = []

    # Search for exe
    for file_name in app_dic['files']:
        if file_name.endswith(".exe"):
            bin_an_dic['bin'] = file_name
            bin_an_dic['bin_name'] = file_name.replace(".exe", "")
            break
    if not bin_an_dic['bin_name']:
        PrintException("[ERROR] No executeable in appx.")

    bin_path = os.path.join(app_dic['app_dir'], bin_an_dic['bin'])

    # Execute strings command
    bin_an_dic['strings'] = ""
    str_list = list(set(strings_util(bin_path)))  # Make unique # pylint: disable-msg=R0204
    str_list = [escape(s) for s in str_list]
    bin_an_dic['strings'] = str_list

    # Search for unsave function
    pattern = re.compile("(alloca|gets|memcpy|printf|scanf|sprintf|sscanf|strcat|StrCat|strcpy|StrCpy|strlen|StrLen|strncat|StrNCat|strncpy|StrNCpy|strtok|swprintf|vsnprintf|vsprintf|vswprintf|wcscat|wcscpy|wcslen|wcsncat|wcsncpy|wcstok|wmemcpy)")
    for elem in str_list:
        if pattern.match(elem[5:-5]):
            result = {
                "rule_id": 'Possible Insecure Function',
                "status": 'Insecure',
                "desc": "Possible Insecure Function detected: {}".format(elem[5:-5])
            }
            bin_an_dic['results'].append(result)

    # Execute binskim analysis if vm is available
    if platform.system() != 'Windows':
        if settings.WINDOWS_VM_IP:
            logger.info("Windows VM configured.")
            global proxy
            proxy = xmlrpc.client.ServerProxy(  # pylint: disable-msg=C0103
                "http://{}:{}".format(
                    settings.WINDOWS_VM_IP,
                    settings.WINDOWS_VM_PORT
                )
            )
            name = _upload_sample(bin_path)
            bin_an_dic = __binskim(name, bin_an_dic)
            bin_an_dic = __binscope(name, bin_an_dic)
        else:
            logger.warning("Windows VM not configured in settings.py. Skipping Binskim and Binscope.")
            warning = {
                "rule_id": "VM",
                "status": "Info",
                "info": "",
                "desc": "VM is not configured. Please read the readme.md in MobSF/install/windows."
            }
            bin_an_dic['results'].append(warning)
    else:
        logger.info("Running lokal analysis.")

        global config
        config = configparser.ConfigParser()
        # Switch to settings definded path if available
        config.read(expanduser("~") + "\\MobSF\\Config\\config.txt")

        # Run analysis functions
        bin_an_dic = __binskim(bin_path, bin_an_dic,
                               run_local=True, app_dir=app_dic['app_dir'])
        bin_an_dic = __binscope(bin_path, bin_an_dic,
                                run_local=True, app_dir=app_dic['app_dir'])

    return bin_an_dic