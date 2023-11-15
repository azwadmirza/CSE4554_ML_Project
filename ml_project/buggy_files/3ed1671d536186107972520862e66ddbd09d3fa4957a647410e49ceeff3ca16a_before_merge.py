    def __init__(self, base_url, access_token):
        """
        :param base_url: The base URL of the Canvas instance's API.
        :type base_url: str
        :param access_token: The API key to authenticate requests with.
        :type access_token: str
        """
        new_url = get_institution_url(base_url)

        if 'api/v1' in base_url:
            warnings.warn(
                "`base_url` no longer requires an API version be specified. "
                "Rewriting `base_url` to {}".format(new_url),
                DeprecationWarning
            )
        base_url = new_url + '/api/v1/'

        self.__requester = Requester(base_url, access_token)