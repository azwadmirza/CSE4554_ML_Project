    async def get_user(self, user_id):
        try:
            return await run_concurrently(lambda: self.get_client().users.get(user_id))
        except Exception as e:
            print_exception('Failed to retrieve user {}: {}'.format(user_id, e))
            return None