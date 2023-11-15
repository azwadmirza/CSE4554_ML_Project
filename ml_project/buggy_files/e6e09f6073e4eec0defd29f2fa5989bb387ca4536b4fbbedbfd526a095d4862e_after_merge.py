def extract_archive(path, to_directory=".", merge_single=True, extractor=None):
    path = os.path.abspath(path)
    mode = None
    logger.debug("Extracting %s to %s", path, to_directory)

    if extractor is None:
        if path.endswith(".tar.gz") or path.endswith(".tgz"):
            extractor = "tgz"
        elif path.endswith(".tar.xz") or path.endswith(".txz"):
            extractor = "txz"
        elif path.endswith(".tar"):
            extractor = "tar"
        elif path.endswith(".tar.bz2") or path.endswith(".tbz"):
            extractor = "bz2"
        elif path.endswith(".gz"):
            extractor = "gzip"
        elif path.endswith(".exe"):
            extractor = "exe"
        elif is_7zip_supported(path, None):
            extractor = None
        else:
            raise RuntimeError(
                "Could not extract `%s` - no appropriate extractor found" % path
            )

    if extractor == "tgz":
        opener, mode = tarfile.open, "r:gz"
    elif extractor == "txz":
        opener, mode = tarfile.open, "r:xz"
    elif extractor == "tar":
        opener, mode = tarfile.open, "r:"
    elif extractor == "bz2":
        opener, mode = tarfile.open, "r:bz2"
    elif extractor == "gzip":
        decompress_gz(path, to_directory)
        return
    elif extractor == "gog":
        opener = "innoextract"
    elif extractor == "exe":
        opener = "exe"
    elif extractor is None or is_7zip_supported(path, extractor):
        opener = "7zip"
    else:
        raise RuntimeError("Could not extract `%s` - unknown format specified" % path)

    temp_name = ".extract-" + str(uuid.uuid4())[:8]
    temp_path = temp_dir = os.path.join(to_directory, temp_name)
    try:
        _do_extract(path, temp_path, opener, mode, extractor)
    except (OSError, zlib.error, tarfile.ReadError, EOFError) as ex:
        logger.error("Extraction failed: %s", ex)
        raise ExtractFailure(str(ex))
    if merge_single:
        extracted = os.listdir(temp_path)
        if len(extracted) == 1:
            temp_path = os.path.join(temp_path, extracted[0])

    if os.path.isfile(temp_path):
        destination_path = os.path.join(to_directory, extracted[0])
        if os.path.isfile(destination_path):
            logger.warning("Overwrite existing file %s", destination_path)
            os.remove(destination_path)
        shutil.move(temp_path, to_directory)
        os.removedirs(temp_dir)
    else:
        for archive_file in os.listdir(temp_path):
            source_path = os.path.join(temp_path, archive_file)
            destination_path = os.path.join(to_directory, archive_file)
            # logger.debug("Moving extracted files from %s to %s", source_path, destination_path)

            if system.path_exists(destination_path):
                logger.warning("Overwrite existing path %s", destination_path)
                if os.path.isfile(destination_path):
                    os.remove(destination_path)
                    shutil.move(source_path, destination_path)
                elif os.path.isdir(destination_path):
                    try:
                        system.merge_folders(source_path, destination_path)
                    except OSError as ex:
                        logger.error(
                            "Failed to merge to destination %s: %s",
                            destination_path,
                            ex,
                        )
                        raise ExtractFailure(str(ex))
            else:
                shutil.move(source_path, destination_path)
        system.remove_folder(temp_dir)
    logger.debug("Finished extracting %s to %s", path, to_directory)
    return path, to_directory