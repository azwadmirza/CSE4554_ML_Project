def is_image_name_id(name):
    """Checks whether the given image name is in fact an image ID (hash)."""
    if re.match('^sha256:[0-9a-fA-F]{64}$', name):
        return True
    return False