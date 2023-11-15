def win_fix_java(tools_dir):
    """Runn JAVA path fix in Windows"""
    try:
        logger.info("Running JAVA path fix in Windows")
        dmy = os.path.join(tools_dir, 'd2j2/d2j_invoke.tmp')
        org = os.path.join(tools_dir, 'd2j2/d2j_invoke.bat')
        dat = ''
        with open(dmy, 'r') as file_pointer:
            dat = file_pointer.read().replace("[xxx]", settings.JAVA_PATH + "java")
        with open(org, 'w') as file_pointer:
            file_pointer.write(dat)
    except:
        PrintException("[ERROR] Running JAVA path fix in Windows")