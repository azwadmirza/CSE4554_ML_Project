    def __init__(self, metadata=None, thread_config=4, **kwargs):

        self.storageaccounts = StorageAccountsConfig(thread_config=thread_config)
        self.monitor = MonitorConfig(thread_config=thread_config)
        self.sqldatabase = SQLDatabaseConfig(thread_config=thread_config)
        self.securitycenter = SecurityCenterConfig(thread_config=thread_config)
        self.network = NetworkConfig(thread_config=thread_config)
        self.keyvault = KeyVaultConfig(thread_config=thread_config)

        try:
            self.appgateway = AppGatewayConfig(thread_config=thread_config)
        except NameError:
            pass
        try:
            self.rediscache = RedisCacheConfig(thread_config=thread_config)
        except NameError:
            pass
        try:
            self.appservice = AppServiceConfig(thread_config=thread_config)
        except NameError:
            pass