def FindVbox(debug=False):
    try:
        if settings.ANDROID_DYNAMIC_ANALYZER == "MobSF_VM":
            if len(settings.VBOXMANAGE_BINARY) > 0 and isFileExists(settings.VBOXMANAGE_BINARY):
                return settings.VBOXMANAGE_BINARY
            if platform.system() == "Windows":
                # Path to VBoxManage.exe
                vbox_path = ["C:\Program Files\Oracle\VirtualBox\VBoxManage.exe",
                             "C:\Program Files (x86)\Oracle\VirtualBox\VBoxManage.exe"]
                for path in vbox_path:
                    if os.path.isfile(path):
                        return path
            else:
                # Path to VBoxManage in Linux/Mac
                vbox_path = ["/usr/bin/VBoxManage",
                             "/usr/local/bin/VBoxManage"]
                for path in vbox_path:
                    if os.path.isfile(path):
                        return path
            if debug:
                logger.warning("Could not find VirtualBox path.")
    except:
        if debug:
            PrintException("Cannot find VirtualBox path.")