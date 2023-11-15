    def _recipe_files_to_upload(self, ref, policy, the_files, remote, remote_manifest,
                                local_manifest):
        self._remote_manager.check_credentials(remote)
        remote_snapshot = self._remote_manager.get_recipe_snapshot(ref, remote)
        files_to_upload = {filename.replace("\\", "/"): path
                           for filename, path in the_files.items()}
        if not remote_snapshot:
            return files_to_upload, set()

        deleted = set(remote_snapshot).difference(the_files)
        if policy != UPLOAD_POLICY_FORCE:
            if remote_manifest is None:
                # This is the weird scenario, we have a snapshot but don't have a manifest.
                # Can be due to concurrency issues, so we can try retrieve it now
                try:
                    remote_manifest, _ = self._remote_manager.get_recipe_manifest(ref, remote)
                except NotFoundException:
                    # This is weird, the manifest still not there, better upload everything
                    self._user_io.out.warn("The remote recipe doesn't have the 'conanmanifest.txt' "
                                           "file and will be uploaded: '{}'".format(ref))
                    return files_to_upload, deleted

            if remote_manifest == local_manifest:
                return None, None

            if policy in (UPLOAD_POLICY_NO_OVERWRITE, UPLOAD_POLICY_NO_OVERWRITE_RECIPE):
                raise ConanException("Local recipe is different from the remote recipe. "
                                     "Forbidden overwrite.")

        return files_to_upload, deleted