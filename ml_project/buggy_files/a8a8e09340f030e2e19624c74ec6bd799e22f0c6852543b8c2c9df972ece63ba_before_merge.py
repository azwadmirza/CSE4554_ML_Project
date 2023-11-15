def _get_rest_store(store_uri, **_):
    def get_default_host_creds():
        return rest_utils.MlflowHostCreds(
            host=store_uri,
            username=os.environ.get(_TRACKING_USERNAME_ENV_VAR),
            password=os.environ.get(_TRACKING_PASSWORD_ENV_VAR),
            token=os.environ.get(_TRACKING_TOKEN_ENV_VAR),
            ignore_tls_verification=os.environ.get(_TRACKING_INSECURE_TLS_ENV_VAR) == 'true',
            client_cert_path=os.environ.get(_TRACKING_CLIENT_CERT_PATH_ENV_VAR),
            server_cert_path=os.environ.get(_TRACKING_SERVER_CERT_PATH_ENV_VAR),
        )

    return RestStore(get_default_host_creds)