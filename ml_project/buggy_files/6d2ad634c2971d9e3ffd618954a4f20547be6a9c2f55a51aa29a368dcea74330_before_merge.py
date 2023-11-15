def install_environment(
        prefix: Prefix,
        version: str,
        additional_dependencies: Sequence[str],
) -> None:
    helpers.assert_version_default('golang', version)
    directory = prefix.path(
        helpers.environment_dir(ENVIRONMENT_DIR, C.DEFAULT),
    )

    with clean_path_on_failure(directory):
        remote = git.get_remote_url(prefix.prefix_dir)
        repo_src_dir = os.path.join(directory, 'src', guess_go_dir(remote))

        # Clone into the goenv we'll create
        helpers.run_setup_cmd(prefix, ('git', 'clone', '.', repo_src_dir))

        if sys.platform == 'cygwin':  # pragma: no cover
            _, gopath, _ = cmd_output('cygpath', '-w', directory)
            gopath = gopath.strip()
        else:
            gopath = directory
        env = dict(os.environ, GOPATH=gopath)
        env.pop('GOBIN', None)
        cmd_output_b('go', 'get', './...', cwd=repo_src_dir, env=env)
        for dependency in additional_dependencies:
            cmd_output_b('go', 'get', dependency, cwd=repo_src_dir, env=env)
        # Same some disk space, we don't need these after installation
        rmtree(prefix.path(directory, 'src'))
        pkgdir = prefix.path(directory, 'pkg')
        if os.path.exists(pkgdir):  # pragma: no cover (go<1.10)
            rmtree(pkgdir)