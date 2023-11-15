def handle_long_running_operation_exception(ex):
    import json
    import azure.cli.core.telemetry as telemetry

    telemetry.set_exception(
        ex,
        fault_type='failed-long-running-operation',
        summary='Unexpected client exception in {}.'.format(LongRunningOperation.__name__))

    message = getattr(ex, 'message', ex)
    error_message = 'Deployment failed.'

    try:
        correlation_id = ex.response.headers['x-ms-correlation-request-id']
        error_message = '{} Correlation ID: {}.'.format(error_message, correlation_id)
    except:  # pylint: disable=bare-except
        pass

    try:
        inner_message = json.loads(ex.response.text)['error']['details'][0]['message']
        error_message = '{} {}'.format(error_message, inner_message)
    except:  # pylint: disable=bare-except
        error_message = '{} {}'.format(error_message, message)

    cli_error = CLIError(error_message)
    # capture response for downstream commands (webapp) to dig out more details
    setattr(cli_error, 'response', getattr(ex, 'response', None))
    raise cli_error