def copyFile(src_file, dest_file):
    """Copy a file from source to destination.

    :param src_file: Path of source file
    :type src_file: str
    :param dest_file: Path of destination file
    :type dest_file: str
    """
    try:
        from shutil import SpecialFileError, Error
    except ImportError:
        from shutil import Error
        SpecialFileError = Error

    try:
        ek(shutil.copyfile, src_file, dest_file)
    except (SpecialFileError, Error) as error:
        logger.warning(u'{error}', error=error)
    except Exception as error:
        logger.error(u'{error}', error=error)
    else:
        try:
            ek(shutil.copymode, src_file, dest_file)
        except OSError:
            pass