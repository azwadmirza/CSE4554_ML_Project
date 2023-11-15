def apk_2_java(app_path, app_dir, tools_dir):
    """Run jadx."""
    try:
        logger.info('APK -> JAVA')
        args = []
        output = os.path.join(app_dir, 'java_source/')
        logger.info('Decompiling to Java with jadx')

        if os.path.exists(output):
            shutil.rmtree(output)

        if (len(settings.JADX_BINARY) > 0
                and is_file_exists(settings.JADX_BINARY)):
            jadx = settings.JADX_BINARY
        else:
            if platform.system() == 'Windows':
                jadx = os.path.join(tools_dir, 'jadx/bin/jadx.bat')
            else:
                jadx = os.path.join(tools_dir, 'jadx/bin/jadx')
                # Set write permission, if JADX is not executable
                if not os.access(jadx, os.X_OK):
                    os.chmod(jadx, stat.S_IEXEC)
            args = [
                jadx,
                '-ds',
                output,
                '-q',
                '-r',
                '--show-bad-code',
                app_path,
            ]
            fnull = open(os.devnull, 'w')
            subprocess.call(args,
                            stdout=fnull,
                            stderr=subprocess.STDOUT)
    except Exception:
        logger.exception('Decompiling to JAVA')