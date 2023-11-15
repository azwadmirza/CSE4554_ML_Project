    def snow_argument_spec():
        return dict(
            instance=dict(type='str', required=False, fallback=(env_fallback, ['SN_INSTANCE'])),
            username=dict(type='str', required=False, fallback=(env_fallback, ['SN_USERNAME'])),
            password=dict(type='str', required=False, no_log=True, fallback=(env_fallback, ['SN_PASSWORD'])),
            client_id=dict(type='str', no_log=True),
            client_secret=dict(type='str', no_log=True),
        )