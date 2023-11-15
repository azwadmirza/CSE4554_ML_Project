def get_manifest_file(app_path, app_dir, tools_dir):
    """Get readable AndroidManifest.xml"""
    try:
        manifest = None
        if len(settings.APKTOOL_BINARY) > 0 and isFileExists(settings.APKTOOL_BINARY):
            apktool_path = settings.APKTOOL_BINARY
        else:
            apktool_path = os.path.join(tools_dir, 'apktool_2.3.4.jar')
        output_dir = os.path.join(app_dir, "apktool_out")
        args = [settings.JAVA_PATH + 'java', '-jar',
                apktool_path, "--match-original", "-f", "-s", "d", app_path, "-o", output_dir]
        manifest = os.path.join(output_dir, "AndroidManifest.xml")
        if isFileExists(manifest):
            # APKTool already created readable XML
            return manifest
        logger.info("Converting AXML to XML")
        subprocess.check_output(args)
        return manifest
    except:
        PrintException("Getting Manifest file")