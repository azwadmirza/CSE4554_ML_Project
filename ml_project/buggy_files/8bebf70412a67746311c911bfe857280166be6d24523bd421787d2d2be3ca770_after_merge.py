    def __init__(self, **kwargs):
        super(AzCli, self).__init__(**kwargs)

        from azure.cli.core.commands.arm import add_id_parameters
        from azure.cli.core.cloud import get_active_cloud
        from azure.cli.core.extensions import register_extensions
        from azure.cli.core._session import ACCOUNT, CONFIG, SESSION

        import knack.events as events
        from knack.util import ensure_dir

        self.data['headers'] = {}
        self.data['command'] = 'unknown'
        self.data['command_extension_name'] = None
        self.data['completer_active'] = ARGCOMPLETE_ENV_NAME in os.environ
        self.data['query_active'] = False

        azure_folder = self.config.config_dir
        ensure_dir(azure_folder)
        ACCOUNT.load(os.path.join(azure_folder, 'azureProfile.json'))
        CONFIG.load(os.path.join(azure_folder, 'az.json'))
        SESSION.load(os.path.join(azure_folder, 'az.sess'), max_age=3600)
        self.cloud = get_active_cloud(self)
        logger.debug('Current cloud config:\n%s', str(self.cloud.name))

        register_extensions(self)
        self.register_event(events.EVENT_INVOKER_POST_CMD_TBL_CREATE, add_id_parameters)
        # TODO: Doesn't work because args get copied
        # self.register_event(events.EVENT_INVOKER_PRE_CMD_TBL_CREATE, _pre_command_table_create)

        self.progress_controller = None