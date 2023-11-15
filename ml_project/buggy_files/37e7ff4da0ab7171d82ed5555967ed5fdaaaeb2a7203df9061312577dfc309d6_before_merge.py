def save_lang_conf(value):
    """Save language setting to language config file"""
    with open(LANG_FILE, 'w') as f:
        f.write(value)