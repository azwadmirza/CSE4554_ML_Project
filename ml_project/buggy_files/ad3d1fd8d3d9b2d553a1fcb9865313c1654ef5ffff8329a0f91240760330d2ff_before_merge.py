def createUserConfig(MobSF_HOME):
    try:
        CONFIG_PATH = os.path.join(MobSF_HOME, 'config.py')
        if isFileExists(CONFIG_PATH) == False:
            SAMPLE_CONF = os.path.join(settings.BASE_DIR, "MobSF/settings.py")
            with io.open(SAMPLE_CONF, mode='r', encoding="utf8", errors="ignore") as f:
                dat = f.readlines()
            CONFIG = list()
            add = False
            for line in dat:
                if "^CONFIG-START^" in line:
                    add = True
                if "^CONFIG-END^" in line:
                    break
                if add:
                    CONFIG.append(line.lstrip())
            CONFIG.pop(0)
            COMFIG_STR = ''.join(CONFIG)
            with io.open(CONFIG_PATH, mode='w', encoding="utf8", errors="ignore") as f:
                f.write(COMFIG_STR)
    except:
        PrintException("[ERROR] Cannot create config file")