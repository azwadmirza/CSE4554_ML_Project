    def make_local(self, deps):
        def make_local_strategy(directory):
            copy_tree_to_path(resource_filename('empty_template'), directory)
        return self._new_repo(
            'local:{}'.format(','.join(sorted(deps))), C.LOCAL_REPO_VERSION,
            make_local_strategy,
        )