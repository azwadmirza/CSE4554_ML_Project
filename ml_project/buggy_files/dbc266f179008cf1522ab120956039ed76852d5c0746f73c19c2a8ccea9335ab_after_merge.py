    def _recon_repository_from_origin(self, repository_origin):
        check.inst_param(
            repository_origin, 'repository_origin', RepositoryOrigin,
        )

        if isinstance(repository_origin, RepositoryGrpcServerOrigin):
            return ReconstructableRepository(
                self._repository_symbols_and_code_pointers.code_pointers_by_repo_name[
                    repository_origin.repository_name
                ]
            )
        return recon_repository_from_origin(repository_origin)