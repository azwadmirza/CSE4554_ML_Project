    def make_local(self, deps):
        def make_local_strategy(directory):
            copy_tree_to_path(resource_filename('empty_template'), directory)

            env = no_git_env()
            name, email = 'pre-commit', 'asottile+pre-commit@umich.edu'
            env['GIT_AUTHOR_NAME'] = env['GIT_COMMITTER_NAME'] = name
            env['GIT_AUTHOR_EMAIL'] = env['GIT_COMMITTER_EMAIL'] = email

            # initialize the git repository so it looks more like cloned repos
            def _git_cmd(*args):
                cmd_output('git', '-C', directory, *args, env=env)

            _git_cmd('init', '.')
            _git_cmd('config', 'remote.origin.url', '<<unknown>>')
            _git_cmd('add', '.')
            _git_cmd('commit', '--no-edit', '--no-gpg-sign', '-n', '-minit')

        return self._new_repo(
            'local:{}'.format(','.join(sorted(deps))), C.LOCAL_REPO_VERSION,
            make_local_strategy,
        )