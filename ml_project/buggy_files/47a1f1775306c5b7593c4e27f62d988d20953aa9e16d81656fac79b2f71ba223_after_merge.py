    def _check_dvc_filename(fname):
        if not Stage.is_valid_filename(fname):
            raise StageFileBadNameError(
                "bad stage filename '{}'. Stage files should be named"
                " 'Dvcfile' or have a '.dvc' suffix (e.g. '{}.dvc').".format(
                    relpath(fname), os.path.basename(fname)
                )
            )