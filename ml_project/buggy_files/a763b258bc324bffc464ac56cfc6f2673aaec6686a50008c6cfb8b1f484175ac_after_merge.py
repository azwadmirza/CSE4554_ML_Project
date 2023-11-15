    def __init__(self, base_url, access_token):
        """
        :param base_url: The base URL of the Canvas instance's API.
        :type base_url: str
        :param access_token: The API key to authenticate requests with.
        :type access_token: str
        """
        new_url = get_institution_url(base_url)

        if "api/v1" in base_url:
            warnings.warn(
                "`base_url` no longer requires an API version be specified. "
                "Rewriting `base_url` to {}".format(new_url),
                DeprecationWarning,
            )

        if "http://" in base_url:
            warnings.warn(
                "Canvas may respond unexpectedly when making requests to HTTP "
                "URLs. If possible, please use HTTPS.",
                UserWarning,
            )

        if not base_url.strip():
            warnings.warn(
                "Canvas needs a valid URL, please provide a non-blank `base_url`.",
                UserWarning,
            )

        if "://" not in base_url:
            warnings.warn(
                "An invalid `base_url` for the Canvas API Instance was used. "
                "Please provide a valid HTTP or HTTPS URL if possible.",
                UserWarning,
            )

        # Ensure that the user-supplied access token contains no leading or
        # trailing spaces that may cause issues when communicating with
        # the API.
        access_token = access_token.strip()

        base_url = new_url + "/api/v1/"

        self.__requester = Requester(base_url, access_token)