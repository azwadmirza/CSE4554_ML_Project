    def find_from_user_account(self, username, password, tenant, resource):
        context = self._create_auth_context(tenant)
        if password:
            token_entry = context.acquire_token_with_username_password(resource, username, password, _CLIENT_ID)
        else:  # when refresh account, we will leverage local cached tokens
            token_entry = context.acquire_token(resource, username, _CLIENT_ID)

        self.user_id = token_entry[_TOKEN_ENTRY_USER_ID]

        if tenant is None:
            result = self._find_using_common_tenant(token_entry[_ACCESS_TOKEN], resource)
        else:
            result = self._find_using_specific_tenant(tenant, token_entry[_ACCESS_TOKEN])
        return result