    def __init__(self, environment, kwargs):
        Dependency.__init__(self, 'qt4')
        self.name = 'qt4'
        self.root = '/usr'
        self.modules = []
        mods = kwargs.get('modules', [])
        if isinstance(mods, str):
            mods = [mods]
        for module in mods:
            self.modules.append(PkgConfigDependency('Qt' + module, environment, kwargs))
        if len(self.modules) == 0:
            raise DependencyException('No Qt4 modules specified.')