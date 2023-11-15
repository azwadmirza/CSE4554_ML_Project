    def response(self, request, exception):
        """Fetches and executes an exception handler and returns a response
        object

        :param request: Request
        :param exception: Exception to handle
        :return: Response object
        """
        handler = self.handlers.get(type(exception), self.default)
        try:
            response = handler(request=request, exception=exception)
        except Exception:
            self.log(format_exc())
            if self.debug:
                url = getattr(request, 'url', 'unknown')
                response_message = (
                    'Exception raised in exception handler "{}" '
                    'for uri: "{}"\n{}').format(
                        handler.__name__, url, format_exc())
                log.error(response_message)
                return text(response_message, 500)
            else:
                return text('An error occurred while handling an error', 500)
        return response