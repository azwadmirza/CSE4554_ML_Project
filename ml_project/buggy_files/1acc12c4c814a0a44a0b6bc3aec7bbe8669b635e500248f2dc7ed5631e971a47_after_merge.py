    def load(repo, fname):
        fname, tag = Stage._get_path_tag(fname)

        # it raises the proper exceptions by priority:
        # 1. when the file doesn't exists
        # 2. filename is not a DVC-file
        # 3. path doesn't represent a regular file
        Stage._check_file_exists(repo, fname)
        Stage._check_dvc_filename(fname)
        Stage._check_isfile(repo, fname)

        with repo.tree.open(fname) as fd:
            d = load_stage_fd(fd, fname)
        # Making a deepcopy since the original structure
        # looses keys in deps and outs load
        state = copy.deepcopy(d)

        Stage.validate(d, fname=relpath(fname))
        path = os.path.abspath(fname)

        stage = Stage(
            repo=repo,
            path=path,
            wdir=os.path.abspath(
                os.path.join(
                    os.path.dirname(path), d.get(Stage.PARAM_WDIR, ".")
                )
            ),
            cmd=d.get(Stage.PARAM_CMD),
            md5=d.get(Stage.PARAM_MD5),
            locked=d.get(Stage.PARAM_LOCKED, False),
            tag=tag,
            state=state,
        )

        stage.deps = dependency.loadd_from(stage, d.get(Stage.PARAM_DEPS, []))
        stage.outs = output.loadd_from(stage, d.get(Stage.PARAM_OUTS, []))

        return stage