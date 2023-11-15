    async def get_keys(self, region: str):

        try:
            keys = await AWSFacadeUtils.get_all_pages('kms', region, self.session, 'list_keys', 'Keys')
            await get_and_set_concurrently(
                [self._get_and_set_key_policy,
                 self._get_and_set_key_metadata,
                 self._get_and_set_key_aliases],
                keys, region=region)
        except Exception as e:
            print_exception('Failed to get KMS keys: {}'.format(e))
            keys = []
        finally:
            return keys