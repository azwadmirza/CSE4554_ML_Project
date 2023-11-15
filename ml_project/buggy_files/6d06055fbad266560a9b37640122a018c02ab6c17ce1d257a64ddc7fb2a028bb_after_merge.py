    def _validate_output_path(cls, path, stage=None):
        from dvc.dvcfile import is_valid_filename

        if is_valid_filename(path):
            raise cls.IsStageFileError(path)

        if stage:
            abs_path = os.path.join(stage.wdir, path)
            if stage.repo.tree.dvcignore.is_ignored(abs_path):
                check = stage.repo.tree.dvcignore.check_ignore(abs_path)
                raise cls.IsIgnoredError(check)