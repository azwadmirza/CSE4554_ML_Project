    def _request_chain_metadata(self) -> Dict[str, Any]:
        """Subscan API metadata documentation:
        https://docs.api.subscan.io/#metadata
        """
        response = self._request_explorer_api(endpoint='metadata')
        if response.status_code != HTTPStatus.OK:
            message = (
                f'{self.chain} chain metadata request was not successful. '
                f'Response status code: {response.status_code}. '
                f'Response text: {response.text}.',
            )
            log.error(message)
            raise RemoteError(message)
        try:
            result = rlk_jsonloads_dict(response.text)
        except JSONDecodeError as e:
            message = (
                f'{self.chain} chain metadata request returned invalid JSON '
                f'response: {response.text}.',
            )
            log.error(message)
            raise RemoteError(message) from e

        log.debug(f'{self.chain} subscan API metadata', result=result)
        return result