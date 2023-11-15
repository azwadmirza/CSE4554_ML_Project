    def ListRepositories(self, request, _context):
        return api_pb2.ListRepositoriesReply(
            serialized_list_repositories_response=serialize_dagster_namedtuple(
                ListRepositoriesResponse(
                    self._loadable_repository_symbols,
                    executable_path=self._loadable_target_origin.executable_path
                    if self._loadable_target_origin
                    else None,
                    repository_code_pointer_dict=self._repository_code_pointer_dict,
                )
            )
        )