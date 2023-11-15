def from_file(filename):
    url_scheme = filename.split("://", 1)[0]
    if url_scheme in CONDA_SESSION_SCHEMES:
        yamlstr = download_text(filename)
    elif not os.path.exists(filename):
        raise exceptions.EnvironmentFileNotFound(filename)
    else:
        with open(filename, 'r') as fp:
            yamlstr = fp.read()
    return from_yaml(yamlstr, filename=filename)