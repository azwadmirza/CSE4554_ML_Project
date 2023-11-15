def log_api_error(e, client_version):
    if b'client is newer than server' not in e.explanation:
        log.error(e.explanation)
        return

    version = API_VERSION_TO_ENGINE_VERSION.get(client_version)
    if not version:
        # They've set a custom API version
        log.error(e.explanation)
        return

    log.error(
        "The Docker Engine version is less than the minimum required by "
        "Compose. Your current project requires a Docker Engine of "
        "version {version} or greater.".format(version=version))