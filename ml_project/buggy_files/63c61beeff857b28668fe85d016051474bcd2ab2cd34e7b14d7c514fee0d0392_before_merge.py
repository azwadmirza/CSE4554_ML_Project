    def __init__(self, module):
        self.module       = module
        self.name         = module.params['name']
        if self.platform == 'Linux' and Facts(module).is_systemd_managed():
            self.strategy = SystemdStrategy(module)
        else:
            self.strategy = self.strategy_class(module)