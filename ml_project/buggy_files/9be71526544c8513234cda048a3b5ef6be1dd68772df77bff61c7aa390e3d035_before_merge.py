def handle_exception(ex):
    # For error code, follow guidelines at https://docs.python.org/2/library/sys.html#sys.exit,
    from msrestazure.azure_exceptions import CloudError
    from msrest.exceptions import HttpOperationError, ValidationError, ClientRequestError
    from azure.cli.core.azlogging import CommandLoggerContext

    with CommandLoggerContext(logger):

        if isinstance(ex, (CLIError, CloudError)):
            logger.error(ex.args[0])
            return ex.args[1] if len(ex.args) >= 2 else 1
        if isinstance(ex, ValidationError):
            logger.error('validation error: %s', ex)
            return 1
        if isinstance(ex, ClientRequestError):
            logger.error("request failed: %s", ex)
            return 1
        if isinstance(ex, KeyboardInterrupt):
            return 1
        if isinstance(ex, HttpOperationError):
            try:
                response_dict = json.loads(ex.response.text)
                error = response_dict['error']

                # ARM should use ODATA v4. So should try this first.
                # http://docs.oasis-open.org/odata/odata-json-format/v4.0/os/odata-json-format-v4.0-os.html#_Toc372793091
                if isinstance(error, dict):
                    code = "{} - ".format(error.get('code', 'Unknown Code'))
                    message = error.get('message', ex)
                    logger.error("%s%s", code, message)
                else:
                    logger.error(error)

            except (ValueError, KeyError):
                logger.error(ex)
            return 1

        logger.error("The command failed with an unexpected error. Here is the traceback:\n")
        logger.exception(ex)
        logger.warning("\nTo open an issue, please run: 'az feedback'")

        return 1