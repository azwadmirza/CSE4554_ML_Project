    def list_artifacts(self, path=None):
        if path:
            run_relative_path = posixpath.join(
                self.run_relative_artifact_repo_root_path, path)
        else:
            run_relative_path = self.run_relative_artifact_repo_root_path
        infos = []
        page_token = None
        while True:
            if page_token:
                json_body = message_to_json(
                    ListArtifacts(run_id=self.run_id, path=run_relative_path,
                                  page_token=page_token))
            else:
                json_body = message_to_json(
                    ListArtifacts(run_id=self.run_id, path=run_relative_path))
            response = self._call_endpoint(MlflowService, ListArtifacts, json_body)
            artifact_list = response.files
            # If `path` is a file, ListArtifacts returns a single list element with the
            # same name as `path`. The list_artifacts API expects us to return an empty list in this
            # case, so we do so here.
            if len(artifact_list) == 1 and artifact_list[0].path == path \
                    and not artifact_list[0].is_dir:
                return []
            for output_file in artifact_list:
                file_rel_path = posixpath.relpath(
                    path=output_file.path, start=self.run_relative_artifact_repo_root_path)
                artifact_size = None if output_file.is_dir else output_file.file_size
                infos.append(FileInfo(file_rel_path, output_file.is_dir, artifact_size))
            if len(artifact_list) == 0 or not response.next_page_token:
                break
            page_token = response.next_page_token
        return infos