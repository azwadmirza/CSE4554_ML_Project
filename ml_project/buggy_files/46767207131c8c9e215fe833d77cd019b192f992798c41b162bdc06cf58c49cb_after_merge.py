    def load(project, fname):
        if not os.path.exists(fname):
            Stage._check_dvc_file(fname)
            raise StageFileDoesNotExistError(fname)

        Stage._check_dvc_filename(fname)

        if not Stage.is_stage_file(fname):
            Stage._check_dvc_file(fname)
            raise StageFileIsNotDvcFileError(fname)

        with open(fname, 'r') as fd:
            return Stage.loadd(project, yaml.safe_load(fd) or dict(), fname)