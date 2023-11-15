def zipdir(path, zip_file):
    """Zip a directory."""
    try:
        logger.info("Zipping")
        # pylint: disable=unused-variable
        # Needed by os.walk
        for root, _sub_dir, files in os.walk(path):
            for file_name in files:
                zip_file.write(os.path.join(root, file_name))
    except:
        PrintException("[ERROR] Zipping")