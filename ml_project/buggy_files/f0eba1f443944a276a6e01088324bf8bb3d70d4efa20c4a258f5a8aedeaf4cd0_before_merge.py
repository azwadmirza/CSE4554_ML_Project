def class_dump_z(tools_dir, bin_path, app_dir):
    """Running Classdumpz on binary"""
    try:
        webview = {}
        if platform.system() == "Darwin":
            logger.info("Running class-dump-z against the binary for dumping classes")
            if len(settings.CLASSDUMPZ_BINARY) > 0 and isFileExists(settings.CLASSDUMPZ_BINARY):
                class_dump_z_bin = settings.CLASSDUMPZ_BINARY
            else:
                class_dump_z_bin = os.path.join(tools_dir, 'class-dump-z')
            subprocess.call(["chmod", "777", class_dump_z_bin])
            args = [class_dump_z_bin, bin_path]
        elif platform.system() == "Linux":
            logger.info("Running jtool against the binary for dumping classes")
            if len(settings.JTOOL_BINARY) > 0 and isFileExists(settings.JTOOL_BINARY):
                jtool_bin = settings.JTOOL_BINARY
            else:
                jtool_bin = os.path.join(tools_dir, 'jtool.ELF64')
            subprocess.call(["chmod", "777", jtool_bin])
            args = [jtool_bin, '-arch', 'arm', '-d', 'objc', '-v', bin_path]
        else:
            # Platform not supported
            return {}
        classdump = subprocess.check_output(args)
        dump_file = os.path.join(app_dir, "classdump.txt")
        with open(dump_file, "w") as flip:
            flip.write(classdump.decode("utf-8", "ignore"))
        if b"UIWebView" in classdump:
            webview = {"issue": "Binary uses WebView Component.",
                       "status": INFO,
                       "description":  "The binary may use WebView Component."
                       }
        return webview
    except:
        logger.warning("class-dump-z does not work on iOS apps developed in Swift")
        PrintException("[ERROR] - Cannot perform class dump")