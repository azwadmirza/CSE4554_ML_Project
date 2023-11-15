def slugify(value):
    """Remove special characters from a string and slugify it.

    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = str(value)
    # This differs from the Lutris website implementation which uses the Django
    # version of `slugify` and uses the "NFKD" normalization method instead of
    # "NFD". This creates some inconsistencies in titles containing a trademark
    # symbols or some other special characters. The website version of slugify
    # will likely get updated to use the same normalization method.
    value = unicodedata.normalize("NFD", value).encode("ascii", "ignore")
    value = value.decode("utf-8")
    value = str(re.sub(r"[^\w\s-]", "", value)).strip().lower()
    return re.sub(r"[-\s]+", "-", value)