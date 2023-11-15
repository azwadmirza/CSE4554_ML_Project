    def validate_api_key(self) -> Tuple[bool, str]:
        try:
            # We know account endpoint returns a dict
            self.api_query_dict('account')
        except RemoteError as e:
            error = str(e)
            if 'API-key format invalid' in error:
                return False, 'Provided API Key is in invalid Format'
            elif 'Signature for this request is not valid' in error:
                return False, 'Provided API Secret is malformed'
            elif 'Invalid API-key, IP, or permissions for action' in error:
                return False, 'API Key does not match the given secret'
            else:
                raise
        return True, ''