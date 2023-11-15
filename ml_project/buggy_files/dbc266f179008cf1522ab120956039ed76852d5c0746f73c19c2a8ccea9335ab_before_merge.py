    def _recon_repository_from_origin(self, repository_origin):
        check.inst_param(
            repository_origin, 'repository_origin', RepositoryOrigin,
        )

        if isinstance(repository_origin, RepositoryGrpcServerOrigin):
            return ReconstructableRepository(
                self._repository_code_pointer_dict[repository_origin.repository_name]
            )
        return recon_repository_from_origin(repository_origin)