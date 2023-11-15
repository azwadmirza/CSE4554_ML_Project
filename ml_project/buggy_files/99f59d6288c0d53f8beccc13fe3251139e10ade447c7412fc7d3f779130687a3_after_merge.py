    def ListRepositories(self, request, _context):
        try:
            response = ListRepositoriesResponse(
                self._repository_symbols_and_code_pointers.loadable_repository_symbols,
                executable_path=self._loadable_target_origin.executable_path
                if self._loadable_target_origin
                else None,
                repository_code_pointer_dict=(
                    self._repository_symbols_and_code_pointers.code_pointers_by_repo_name
                ),
            )
        except Exception:  # pylint: disable=broad-except
            response = serializable_error_info_from_exc_info(sys.exc_info())

        return api_pb2.ListRepositoriesReply(
            serialized_list_repositories_response_or_error=serialize_dagster_namedtuple(response)
        )