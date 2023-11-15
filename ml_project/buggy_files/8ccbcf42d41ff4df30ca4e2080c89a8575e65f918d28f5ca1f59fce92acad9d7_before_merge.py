def get_extractor_py2(path, format):
    import capa.features.extractors.viv

    vw = get_workspace(path, format)
    return capa.features.extractors.viv.VivisectFeatureExtractor(vw, path)