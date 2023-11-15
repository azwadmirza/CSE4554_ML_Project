def api_key():
    """Print REST API Key"""

    if os.environ.get('MOBSF_API_KEY'):
        logger.info("\nAPI Key read from environment variable")
        return os.environ['MOBSF_API_KEY']

    secret_file = os.path.join(settings.MobSF_HOME, "secret")
    if isFileExists(secret_file):
        try:
            _api_key = open(secret_file).read().strip()
            return gen_sha256_hash(_api_key)
        except Exception:
            PrintException("[ERROR] Cannot Read API Key")