def _validate_natural(value):
    if value <= 0:
        raise exceptions.ApiError(
            'Must be greater than zero',
            status_code=422
        )