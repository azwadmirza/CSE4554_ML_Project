def FindJava(debug=False):
    """ Find Java """
    # Maintain JDK Version
    java_versions = '1.7|1.8|1.9|2.0|2.1|2.2|2.3|8|9|10|11'
    """
    This code is needed because some people are not capable
    of setting java path :-(
    """
    win_java_paths = [
        "C:/Program Files/Java/",
        "C:/Program Files (x86)/Java/",
        "D:/Program Files/Java/",
        "D:/Program Files (x86)/Java/",
        "E:/Program Files/Java/",
        "E:/Program Files (x86)/Java/",
        "F:/Program Files/Java/",
        "F:/Program Files (x86)/Java/",
        "G:/Program Files/Java/",
        "G:/Program Files (x86)/Java/",
        "H:/Program Files/Java/",
        "H:/Program Files (x86)/Java/",
        "I:/Program Files/Java/",
        "I:/Program Files (x86)/Java/",
    ]
    try:
        err_msg1 = "[ERROR] Oracle JDK 1.7 or above is not found!"
        if isDirExists(settings.JAVA_DIRECTORY):
            if settings.JAVA_DIRECTORY.endswith("/"):
                return settings.JAVA_DIRECTORY
            elif settings.JAVA_DIRECTORY.endswith("\\"):
                return settings.JAVA_DIRECTORY
            else:
                return settings.JAVA_DIRECTORY + "/"
        elif platform.system() == "Windows":
            if debug:
                logger.info("Finding JDK Location in Windows....")
            # JDK 7 jdk1.7.0_17/bin/
            for java_path in win_java_paths:
                if os.path.isdir(java_path):
                    for dirname in os.listdir(java_path):
                        if "jdk" in dirname:
                            win_java_path = java_path + dirname + "/bin/"
                            args = [win_java_path + "java", "-version"]
                            dat = RunProcess(args)
                            if "java" in dat:
                                if debug:
                                    logger.info("Oracle Java JDK is installed!")
                                return win_java_path
            for env in ["JDK_HOME", "JAVA_HOME"]:
                java_home = os.environ.get(env)
                if java_home and os.path.isdir(java_home):
                    win_java_path = java_home + "/bin/"
                    args = [win_java_path + "java", "-version"]
                    dat = RunProcess(args)
                    if "java" in dat:
                        if debug:
                            logger.info("Oracle Java is installed!")
                        return win_java_path

            if debug:
                logger.info(err_msg1)
            return "java"
        else:
            if debug:
                logger.info("Finding JDK Location in Linux/MAC....")
            # Check in Environment Variables
            for env in ["JDK_HOME", "JAVA_HOME"]:
                java_home = os.environ.get(env)
                if java_home and os.path.isdir(java_home):
                    lm_java_path = java_home + "/bin/"
                    args = [lm_java_path + "java", "-version"]
                    dat = RunProcess(args)
                    if "oracle" in dat:
                        if debug:
                            logger.info("Oracle Java is installed!")
                        return lm_java_path
            mac_linux_java_dir = "/usr/bin/"
            args = [mac_linux_java_dir + "java"]
            dat = RunProcess(args)
            if "oracle" in dat:
                args = [mac_linux_java_dir + "java", '-version']
                dat = RunProcess(args)
                f_line = dat.split("\n")[0]
                if re.findall(java_versions, f_line):
                    if debug:
                        logger.info("JDK 1.7 or above is available")
                    return mac_linux_java_dir
                else:
                    err_msg = "[ERROR] Please install Oracle JDK 1.7 or above"
                    if debug:
                        logger.error(Color.BOLD + Color.RED + err_msg + Color.END)
                    return "java"
            else:
                args = [mac_linux_java_dir + "java", '-version']
                dat = RunProcess(args)
                f_line = dat.split("\n")[0]
                if re.findall(java_versions, f_line):
                    if debug:
                        logger.info("JDK 1.7 or above is available")
                    return mac_linux_java_dir
                else:
                    err_msg = "Please install Oracle JDK 1.7 or above"
                    if debug:
                        logger.error(Color.BOLD + Color.RED + err_msg + Color.END)
                    return "java"

    except:
        if debug:
            PrintException("[ERROR] Oracle Java (JDK >=1.7) is not found!")
        return "java"