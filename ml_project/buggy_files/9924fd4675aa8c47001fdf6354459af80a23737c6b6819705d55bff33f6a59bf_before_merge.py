def plural(num, singular: str, plural: str = None) -> str:
    return singular if (num == 1 or num == -1) else plural or singular + 's'