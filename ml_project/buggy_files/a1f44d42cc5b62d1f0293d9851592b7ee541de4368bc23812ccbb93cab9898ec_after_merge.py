def copyfile(src, dest, symlink=True):
    if symlink and hasattr(os, "symlink") and not IS_WIN:
        return symlink_file_or_folder(src, dest)
    if not os.path.exists(src):
        # Some bad symlink in the src
        logger.warn("Cannot find file %s (bad symlink)", src)
        return
    if os.path.exists(dest):
        logger.debug("File %s already exists", dest)
        return
    if not os.path.exists(os.path.dirname(dest)):
        logger.info("Creating parent directories for %s", os.path.dirname(dest))
        os.makedirs(os.path.dirname(dest))
    logger.info("Copying to %s", dest)
    copy_file_or_folder(src, dest, symlink)