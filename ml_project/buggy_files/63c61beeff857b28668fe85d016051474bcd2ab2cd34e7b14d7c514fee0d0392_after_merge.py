    def __init__(self, module):
        self.module       = module
        self.name         = module.params['name']
        if self.platform == 'Linux' and ServiceMgrFactCollector.is_systemd_managed(module):
            self.strategy = SystemdStrategy(module)
        else:
            self.strategy = self.strategy_class(module)