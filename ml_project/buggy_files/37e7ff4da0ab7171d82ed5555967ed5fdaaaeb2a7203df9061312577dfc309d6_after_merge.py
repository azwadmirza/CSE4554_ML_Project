def save_lang_conf(value):
    """Save language setting to language config file"""
    # Needed to avoid an error when trying to save LANG_FILE
    # but the operation fails for some reason.
    # See issue 8807
    try:
        with open(LANG_FILE, 'w') as f:
            f.write(value)
    except EnvironmentError:
        pass