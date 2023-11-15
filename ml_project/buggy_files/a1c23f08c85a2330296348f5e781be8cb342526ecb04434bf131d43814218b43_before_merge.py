def dex_2_jar(app_path, app_dir, tools_dir):
    """Run dex2jar."""
    try:
        logger.info("DEX -> JAR")
        working_dir = None
        args = []

        if settings.JAR_CONVERTER == "d2j":
            logger.info("Using JAR converter - dex2jar")
            dexes = get_dex_files(app_dir)
            for idx, dex in enumerate(dexes):
                logger.info("Converting " + dex + " to JAR")
                if len(settings.DEX2JAR_BINARY) > 0 and isFileExists(settings.DEX2JAR_BINARY):
                    d2j = settings.DEX2JAR_BINARY
                else:
                    if platform.system() == "Windows":
                        win_fix_java(tools_dir)
                        d2j = os.path.join(tools_dir, 'd2j2/d2j-dex2jar.bat')
                    else:
                        inv = os.path.join(tools_dir, 'd2j2/d2j_invoke.sh')
                        d2j = os.path.join(tools_dir, 'd2j2/d2j-dex2jar.sh')
                        subprocess.call(["chmod", "777", d2j])
                        subprocess.call(["chmod", "777", inv])
                args = [
                    d2j,
                    dex,
                    '-f',
                    '-o',
                    app_dir + 'classes'+str(idx)+'.jar'
                ]
                subprocess.call(args)

        elif settings.JAR_CONVERTER == "enjarify":
            logger.info("Using JAR converter - Google enjarify")
            if len(settings.ENJARIFY_DIRECTORY) > 0 and isDirExists(settings.ENJARIFY_DIRECTORY):
                working_dir = settings.ENJARIFY_DIRECTORY
            else:
                working_dir = os.path.join(tools_dir, 'enjarify/')
            if platform.system() == "Windows":
                win_fix_python3(tools_dir)
                enjarify = os.path.join(working_dir, 'enjarify.bat')
                args = [enjarify, app_path, "-f",
                        "-o", app_dir + 'classes.jar']
            else:
                if len(settings.PYTHON3_PATH) > 2:
                    python3 = os.path.join(settings.PYTHON3_PATH, "python3")
                else:
                    python3 = get_python()
                args = [
                    python3,
                    "-O",
                    "-m",
                    "enjarify.main",
                    app_path,
                    "-f",
                    "-o",
                    app_dir + 'classes.jar'
                ]
            subprocess.call(args, cwd=working_dir)
    except:
        PrintException("[ERROR] Converting Dex to JAR")