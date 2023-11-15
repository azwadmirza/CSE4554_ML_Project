    async def is_ignored_by(
        self, ignored_user_id: str, ignorer_user_id: str, cache_context: _CacheContext
    ) -> bool:
        ignored_account_data = await self.get_global_account_data_by_type_for_user(
            AccountDataTypes.IGNORED_USER_LIST,
            ignorer_user_id,
            on_invalidate=cache_context.invalidate,
        )
        if not ignored_account_data:
            return False

        try:
            return ignored_user_id in ignored_account_data.get("ignored_users", {})
        except TypeError:
            # The type of the ignored_users field is invalid.
            return False