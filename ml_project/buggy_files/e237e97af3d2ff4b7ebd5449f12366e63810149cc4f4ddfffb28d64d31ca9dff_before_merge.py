def jar_2_java(app_dir, tools_dir):
    """Conver jar to java."""
    try:
        logger.info("JAR -> JAVA")
        jar_files = get_jar_files(app_dir)
        output = os.path.join(app_dir, 'java_source/')
        for jar_path in jar_files:
            logger.info("Decompiling {} to Java Code".format(jar_path))
            if settings.DECOMPILER == 'jd-core':
                if (
                        len(settings.JD_CORE_DECOMPILER_BINARY) > 0 and
                        isFileExists(settings.JD_CORE_DECOMPILER_BINARY)
                ):
                    jd_path = settings.JD_CORE_DECOMPILER_BINARY
                else:
                    jd_path = os.path.join(tools_dir, 'jd-core.jar')
                args = [settings.JAVA_PATH + 'java',
                        '-jar', jd_path, jar_path, output]
            elif settings.DECOMPILER == 'cfr':
                if (
                        len(settings.CFR_DECOMPILER_BINARY) > 0 and
                        isFileExists(settings.CFR_DECOMPILER_BINARY)
                ):
                    jd_path = settings.CFR_DECOMPILER_BINARY
                else:
                    jd_path = os.path.join(tools_dir, 'cfr_0_132.jar')
                args = [settings.JAVA_PATH + 'java', '-jar',
                        jd_path, jar_path, '--outputdir', output, '--silent', 'true']
            elif settings.DECOMPILER == "procyon":
                if (
                        len(settings.PROCYON_DECOMPILER_BINARY) > 0 and
                        isFileExists(settings.PROCYON_DECOMPILER_BINARY)
                ):
                    pd_path = settings.PROCYON_DECOMPILER_BINARY
                else:
                    pd_path = os.path.join(
                        tools_dir, 'procyon-decompiler-0.5.30.jar')
                args = [settings.JAVA_PATH + 'java',
                        '-jar', pd_path, jar_path, '-o', output]
            subprocess.call(args)
    except:
        PrintException("[ERROR] Converting JAR to JAVA")