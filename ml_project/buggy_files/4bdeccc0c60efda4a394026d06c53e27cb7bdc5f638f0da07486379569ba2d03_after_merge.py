def get_scm(conanfile, src_folder):
    data = getattr(conanfile, "scm", None)
    if data is not None and isinstance(data, dict):
        return SCM(data, src_folder)
    else:
        # not an instance of dict or None, skip SCM feature.
        pass