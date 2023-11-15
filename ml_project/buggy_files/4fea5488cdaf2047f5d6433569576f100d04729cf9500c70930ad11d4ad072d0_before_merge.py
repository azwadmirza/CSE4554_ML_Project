    def _upload_recipe(self, ref, conanfile, retry, retry_wait, policy, remote):
        if policy != UPLOAD_POLICY_FORCE:
            remote_manifest = self._check_recipe_date(ref, remote)
        else:
            remote_manifest = None

        current_remote = self._registry.refs.get(ref)

        if remote != current_remote:
            complete_recipe_sources(self._remote_manager, self._cache, conanfile, ref)

        conanfile_path = self._cache.conanfile(ref)
        self._hook_manager.execute("pre_upload_recipe", conanfile_path=conanfile_path,
                                   reference=ref, remote=remote)

        t1 = time.time()
        the_files = self._compress_recipe_files(ref)
        if policy == UPLOAD_POLICY_SKIP:
            return ref
        files_to_upload, deleted = self._recipe_files_to_upload(ref, policy, the_files,
                                                                remote, remote_manifest)
        if files_to_upload or deleted:
            self._remote_manager.upload_recipe(ref, files_to_upload, deleted,
                                               remote, retry, retry_wait)
            self._upload_recipe_end_msg(ref, remote)
        else:
            self._user_io.out.info("Recipe is up to date, upload skipped")
        duration = time.time() - t1
        log_recipe_upload(ref, duration, the_files, remote.name)
        self._hook_manager.execute("post_upload_recipe", conanfile_path=conanfile_path,
                                   reference=ref, remote=remote)

        # The recipe wasn't in the registry or it has changed the revision field only
        if not current_remote:
            self._registry.refs.set(ref, remote.name)

        return ref