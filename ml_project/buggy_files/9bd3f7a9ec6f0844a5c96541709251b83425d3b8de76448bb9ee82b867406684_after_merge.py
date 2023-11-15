def download_dir():
    """Get the download directory to use."""
    directory = config.val.downloads.location.directory
    remember_dir = config.val.downloads.location.remember

    if remember_dir and last_used_directory is not None:
        ddir = last_used_directory
    elif directory is None:
        ddir = standarddir.download()
    else:
        ddir = directory

    try:
        os.makedirs(ddir, exist_ok=True)
    except OSError as e:
        message.error("Failed to create download directory: {}".format(e))

    return ddir