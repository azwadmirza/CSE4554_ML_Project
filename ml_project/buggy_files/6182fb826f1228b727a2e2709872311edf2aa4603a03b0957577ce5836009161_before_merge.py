def replace_floats_with_decimals(obj: Union[List, Dict], round_digits: int = 9) -> Any:
    """
    Utility method to recursively walk a dictionary or list converting all `float` to `Decimal` as required by DynamoDb.

    Args:
        obj: A `List` or `Dict` object.
        round_digits: A int value to set the rounding precision of Decimal values.

    Returns: An object with all matching values and `float` types replaced by `Decimal`s rounded to `round_digits` decimal places.

    """
    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = replace_floats_with_decimals(obj[i], round_digits)
        return obj
    elif isinstance(obj, dict):
        for j in obj:
            obj[j] = replace_floats_with_decimals(obj[j], round_digits)
        return obj
    elif isinstance(obj, float) or isinstance(obj, Decimal):
        return round(Decimal(obj), round_digits)
    else:
        return obj