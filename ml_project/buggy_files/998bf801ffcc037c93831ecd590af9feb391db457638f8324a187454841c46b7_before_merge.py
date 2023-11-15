    def _recipe_files_to_upload(self, ref, policy, the_files, remote, remote_manifest):
        # Get the remote snapshot
        self._remote_manager.check_credentials(remote)
        remote_snapshot = self._remote_manager.get_recipe_snapshot(ref, remote)

        if remote_snapshot and policy != UPLOAD_POLICY_FORCE:
            local_manifest = FileTreeManifest.loads(load(the_files["conanmanifest.txt"]))

            if remote_manifest == local_manifest:
                return None, None

            if policy in (UPLOAD_POLICY_NO_OVERWRITE, UPLOAD_POLICY_NO_OVERWRITE_RECIPE):
                raise ConanException("Local recipe is different from the remote recipe. "
                                     "Forbidden overwrite.")

        files_to_upload = {filename.replace("\\", "/"): path
                           for filename, path in the_files.items()}
        deleted = set(remote_snapshot).difference(the_files)
        return files_to_upload, deleted