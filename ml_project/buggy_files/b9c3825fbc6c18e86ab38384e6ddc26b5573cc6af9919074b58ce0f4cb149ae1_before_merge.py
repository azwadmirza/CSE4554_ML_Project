def file_or_url_context(resource_name):
    """Yield name of file from the given resource (i.e. file or url)."""
    if is_url(resource_name):
        _, ext = os.path.splitext(resource_name)
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as f:
                u = urlopen(resource_name)
                f.write(u.read())
            # f must be closed before yielding
            yield f.name
        finally:
            os.remove(f.name)
    else:
        yield resource_name