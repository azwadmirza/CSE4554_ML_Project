def is_url(resource_name: Text) -> bool:
    """Check whether the url specified is a well formed one.

    Regex adapted from https://stackoverflow.com/a/7160778/3001665

    Args:
        resource_name: Remote URL to validate

    Returns: `True` if valid, otherwise `False`.
    """
    URL_REGEX = re.compile(
        r"^(?:http|ftp|file)s?://"  # http:// or https:// or file://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return URL_REGEX.match(resource_name) is not None