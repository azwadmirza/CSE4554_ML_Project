def log_api_error(e, client_version):
    explanation = e.explanation
    if isinstance(explanation, six.binary_type):
        explanation = explanation.decode('utf-8')

    if 'client is newer than server' not in explanation:
        log.error(explanation)
        return

    version = API_VERSION_TO_ENGINE_VERSION.get(client_version)
    if not version:
        # They've set a custom API version
        log.error(explanation)
        return

    log.error(
        "The Docker Engine version is less than the minimum required by "
        "Compose. Your current project requires a Docker Engine of "
        "version {version} or greater.".format(version=version))