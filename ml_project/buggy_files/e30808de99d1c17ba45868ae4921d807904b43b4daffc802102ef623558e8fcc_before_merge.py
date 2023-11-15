    def _vault_archive_response_post(self, vault_name, body, querystring, headers):
        vault = self.backend.get_vault(vault_name)
        vault_id = vault.create_archive(body)
        headers['x-amz-archive-id'] = vault_id
        return 201, headers, ""