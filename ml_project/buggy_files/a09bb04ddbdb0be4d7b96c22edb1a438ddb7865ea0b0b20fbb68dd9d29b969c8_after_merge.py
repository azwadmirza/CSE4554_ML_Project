def _read_buckets_cache_file(cache_file):
    """
    Return the contents of the buckets cache file
    """

    log.debug("Reading buckets cache file")

    with salt.utils.files.fopen(cache_file, "rb") as fp_:
        try:
            data = pickle.load(fp_)
        except (
            pickle.UnpicklingError,
            AttributeError,
            EOFError,
            ImportError,
            IndexError,
            KeyError,
            ValueError,
        ) as exc:
            log.debug("Exception reading buckets cache file: '{}'".format(exc))
            data = None

    return data