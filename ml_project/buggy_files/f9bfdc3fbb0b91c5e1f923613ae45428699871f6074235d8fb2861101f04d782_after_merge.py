def report_error(error, request=None, extra_data=None, level='warning',
                 prefix='Handled exception'):
    """Wrapper for error reporting

    This can be used for store exceptions in error reporting solutions as
    rollbar while handling error gracefully and giving user cleaner message.
    """
    if HAS_ROLLBAR and hasattr(settings, 'ROLLBAR'):
        rollbar.report_exc_info(
            request=request, extra_data=extra_data, level=level
        )

    if HAS_RAVEN and hasattr(settings, 'RAVEN_CONFIG'):
        raven_client.captureException(
            request=request, extra=extra_data, level=level
        )

    LOGGER.error(
        '%s: %s: %s',
        prefix,
        error.__class__.__name__,
        force_text(error)
    )