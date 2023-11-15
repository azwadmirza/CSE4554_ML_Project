    def __init__(self, module):
        self.module = module
        self._icinga2 = module.get_bin_path('icinga2', True)