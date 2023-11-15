    def _validate_output_path(cls, path, stage=None):
        from dvc.dvcfile import is_valid_filename

        if is_valid_filename(path):
            raise cls.IsStageFileError(path)

        if stage:
            check = stage.repo.tree.dvcignore.check_ignore(path)
            if check.match:
                raise cls.IsIgnoredError(check)