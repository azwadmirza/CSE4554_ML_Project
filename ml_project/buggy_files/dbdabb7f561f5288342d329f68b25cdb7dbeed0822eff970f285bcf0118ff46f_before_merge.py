def read_manifest(app_dir, app_path, tools_dir, typ, apk):
    """Read the manifest file."""
    try:
        dat = ''
        manifest = ''
        if apk:
            manifest = get_manifest_file(app_path, app_dir, tools_dir)
            if isFileExists(manifest):
                logger.info("Reading Android Manifest")
                with io.open(
                    manifest,
                    mode='r',
                    encoding="utf8",
                    errors="ignore"
                ) as file_pointer:
                    dat = file_pointer.read()
        else:
            logger.info("Reading Manifest from Source")
            if typ == "eclipse":
                manifest = os.path.join(app_dir, "AndroidManifest.xml")
            elif typ == "studio":
                manifest = os.path.join(
                    app_dir, "app/src/main/AndroidManifest.xml"
                )
            with io.open(
                manifest,
                mode='r',
                encoding="utf8",
                errors="ignore"
            ) as file_pointer:
                dat = file_pointer.read()
        return dat
    except:
        PrintException("[ERROR] Reading Manifest file")