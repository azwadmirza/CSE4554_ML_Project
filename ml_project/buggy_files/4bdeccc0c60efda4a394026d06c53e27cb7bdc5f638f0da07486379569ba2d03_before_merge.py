def get_scm(conanfile, src_folder):
    data = getattr(conanfile, "scm", None)
    if data is not None:
        return SCM(data, src_folder)