def from_file(filename):
    url_scheme = filename.split("://", 1)[0]
    if url_scheme in CONDA_SESSION_SCHEMES:
        yamlstr = download_text(filename)
    elif not os.path.exists(filename):
        raise exceptions.EnvironmentFileNotFound(filename)
    else:
        with open(filename, 'rb') as fp:
            yamlb = fp.read()
            try:
                yamlstr = yamlb.decode('utf-8')
            except UnicodeDecodeError:
                yamlstr = yamlb.decode('utf-16')
    return from_yaml(yamlstr, filename=filename)