    def from_filename(cls, path):
        # type: (str) -> ProjectNameAndVersion
        # Handle wheels:
        #
        # The wheel filename convention is specified here:
        #   https://www.python.org/dev/peps/pep-0427/#file-name-convention.
        if path.endswith(".whl"):
            project_name, version, _ = os.path.basename(path).split("-", 2)
            return cls(project_name=project_name, version=version)

        # Handle sdists:
        #
        # The sdist name format has no accepted specification yet, but there is a proposal here:
        #   https://www.python.org/dev/peps/pep-0625/#specification.
        #
        # We do the best we can to support the current landscape. A version number can technically
        # contain a dash though, even under the standards, in un-normalized form:
        #   https://www.python.org/dev/peps/pep-0440/#pre-release-separators.
        # For those cases this logic will produce incorrect results and it does not seem there is
        # much we can do since both project names and versions can contain both alphanumeric
        # characters and dashes.
        fname = _strip_sdist_path(path)
        if fname is not None:
            project_name, version = fname.rsplit("-", 1)
            return cls(project_name=project_name, version=version)

        raise MetadataError(
            "The distribution at path {!r} does not have a file name matching known sdist or wheel "
            "file name formats.".format(path)
        )