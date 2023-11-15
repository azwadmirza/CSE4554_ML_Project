def _validate_natural(value):
    if value < 0:
        raise exceptions.ApiError(
            'Must be a natural number',
            status_code=422
        )