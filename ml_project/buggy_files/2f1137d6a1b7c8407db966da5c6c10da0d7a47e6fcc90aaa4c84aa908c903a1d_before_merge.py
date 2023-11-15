    def check_response_status(self, response):
        """
        Check response status and throw corresponding exception on failure
        """
        code = response.status_code
        if code < 200 or code >= 300:
            try:
                message = response.json()["error"]
            except Exception:
                message = " "

            logger.debug(f'Error received: status code: {code}, message: "{message}"')
            if code == 400:
                raise BadRequestException(response)
            elif response.status_code == 401:
                raise AuthenticationException()
            elif response.status_code == 403:
                raise AuthorizationException()
            elif response.status_code == 404:
                raise NotFoundException()
            elif response.status_code == 429:
                raise OverLimitException(message)
            elif response.status_code == 502:
                raise BadGatewayException()
            elif response.status_code == 504:
                raise GatewayTimeoutException(message)
            elif response.status_code == 423:
                raise LockedException(message)
            elif 500 <= response.status_code < 600:
                if "Server under maintenance" in response.content.decode():
                    raise ServerException(
                        "Server under maintenance, please try again later."
                    )
                else:
                    raise ServerException()
            else:
                msg = "An error occurred. Server response: {}".format(
                    response.status_code
                )
                raise HubException(message=msg)