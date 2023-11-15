def get_extractor_py2(path, format):
    import capa.features.extractors.viv

    vw = get_workspace(path, format, should_save=False)

    try:
        vw.saveWorkspace()
    except IOError:
        # see #168 for discussion around how to handle non-writable directories
        logger.info("source directory is not writable, won't save intermediate workspace")

    return capa.features.extractors.viv.VivisectFeatureExtractor(vw, path)