    def snow_argument_spec():
        return dict(
            instance=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            client_id=dict(type='str', no_log=True),
            client_secret=dict(type='str', no_log=True),
        )