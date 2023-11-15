    def _sync_data_from_server_and_replace_local(self) -> bool:
        """
        Performs syncing of data from server and replaces local db

        Returns true for success and False for error/failure

        May raise:
        - PremiumAuthenticationError due to an UnableToDecryptRemoteData
        coming from  decompress_and_decrypt_db. This happens when the given password
        does not match the one on the saved DB.
        """
        assert self.premium, 'This function has to be called with a not None premium'
        try:
            result = self.premium.pull_data()
        except RemoteError as e:
            log.debug('sync from server -- pulling failed.', error=str(e))
            return False

        if result['data'] is None:
            log.debug('sync from server -- no data found.')
            return False

        try:
            self.data.decompress_and_decrypt_db(self.password, result['data'])
        except UnableToDecryptRemoteData:
            raise PremiumAuthenticationError(
                'The given password can not unlock the database that was retrieved  from '
                'the server. Make sure to use the same password as when the account was created.',
            )

        return True